import base64
from datetime import date
from decimal import Decimal
import io
from django.db import models
import qrcode


def make_upi_qr_data_url(upi_id, name, amount, ref=""):
    if not upi_id:
        return ""
    try:
        uri = f"upi://pay?pa={upi_id.strip()}&pn={name.strip()}&am={amount}&cu=INR&tn={ref}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return ""


def number_to_words_indian(num):
    try:
        val = int(round(num))
        if val <= 0:
            return "Zero Rupees Only"

        units = [
            "",
            "One",
            "Two",
            "Three",
            "Four",
            "Five",
            "Six",
            "Seven",
            "Eight",
            "Nine",
            "Ten",
            "Eleven",
            "Twelve",
            "Thirteen",
            "Fourteen",
            "Fifteen",
            "Sixteen",
            "Seventeen",
            "Eighteen",
            "Nineteen",
        ]
        tens = [
            "",
            "",
            "Twenty",
            "Thirty",
            "Forty",
            "Fifty",
            "Sixty",
            "Seventy",
            "Eighty",
            "Ninety",
        ]

        def _two(n):
            if n < 20:
                return units[n]
            return (tens[n // 10] + (" " + units[n % 10] if n % 10 else "")).strip()

        def _three(n):
            h = n // 100
            r = n % 100
            res = ""
            if h:
                res += units[h] + " Hundred"
            if r:
                res += (" " if res else "") + _two(r)
            return res

        crore = val // 10000000
        val %= 10000000
        lakh = val // 100000
        val %= 100000
        thousand = val // 1000
        val %= 1000

        parts = []
        if crore:
            parts.append(_three(crore) + " Crore")
        if lakh:
            parts.append(_two(lakh) + " Lakh")
        if thousand:
            parts.append(_two(thousand) + " Thousand")
        if val:
            parts.append(_three(val))

        return "Rupees " + " ".join(parts) + " Only"
    except Exception:
        return ""


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    business_category = models.CharField(max_length=100, blank=True)
    gstin = models.CharField(max_length=50, blank=True, help_text="Customer GSTIN")
    shopping_details = models.TextField(blank=True)

    def total_billed(self):
        invoices = Invoice.objects.filter(quotation__customer=self)
        return sum(inv.total_amount() for inv in invoices)

    def total_paid(self):
        invoices = Invoice.objects.filter(quotation__customer=self)
        return sum(inv.paid_amount() for inv in invoices)

    def balance_due(self):
        return max(Decimal("0.00"), self.total_billed() - self.total_paid())

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    hsn_code = models.CharField(
        max_length=20, blank=True, help_text="HSN or SAC Code for GST"
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        help_text="Default GST rate for this item (e.g., 18 for 18%)",
    )

    def __str__(self):
        return self.name


class Term(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class Quotation(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Sent", "Sent"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Expired", "Expired"),
        ("Converted", "Converted"),
    ]

    TAX_TYPE_CHOICES = [
        ("CGST_SGST", "CGST + SGST (Intra-state)"),
        ("IGST", "IGST (Inter-state)"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quote_number = models.CharField(
        max_length=50, blank=True, help_text="e.g. QTN-0001"
    )
    date = models.DateField(
        default=date.today, help_text="Quotation date (defaults to today)"
    )
    valid_until = models.DateField(
        null=True, blank=True, help_text="Quotation validity expiry date"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    po_number = models.CharField(
        max_length=50, blank=True, help_text="Purchase Order Number"
    )
    po_date = models.DateField(null=True, blank=True)
    tax_type = models.CharField(
        max_length=20, choices=TAX_TYPE_CHOICES, default="CGST_SGST"
    )
    items = models.ManyToManyField(Item, through="QuotationItem")
    terms = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Fallback global GST percentage",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Flat discount on subtotal",
    )
    notes = models.TextField(blank=True, help_text="Custom notes / terms for client")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.quote_number:
            self.quote_number = f"QTN-{self.id:04d}"
            super().save(update_fields=["quote_number"])

    def subtotal(self):
        total = Decimal("0.00")
        for qi in self.quotationitem_set.all():
            total += qi.total
        return total

    def subtotal_after_discount(self):
        sub = self.subtotal()
        disc = self.discount_amount or Decimal("0.00")
        return max(Decimal("0.00"), sub - disc)

    def tax_amount(self):
        items = self.quotationitem_set.all()
        if items.exists():
            return sum((qi.tax_amount() for qi in items), Decimal("0.00")).quantize(Decimal("0.01"))
        if not self.gst_percent:
            return Decimal("0.00")
        return (
            self.subtotal_after_discount() * (self.gst_percent / Decimal("100.00"))
        ).quantize(Decimal("0.01"))

    def cgst(self):
        if self.tax_type == "IGST":
            return Decimal("0.00")
        items = self.quotationitem_set.all()
        if items.exists():
            return sum((qi.cgst_amount() for qi in items), Decimal("0.00")).quantize(Decimal("0.01"))
        return (self.tax_amount() / Decimal("2")).quantize(Decimal("0.01"))

    def sgst(self):
        if self.tax_type == "IGST":
            return Decimal("0.00")
        items = self.quotationitem_set.all()
        if items.exists():
            return sum((qi.sgst_amount() for qi in items), Decimal("0.00")).quantize(Decimal("0.01"))
        return (self.tax_amount() - self.cgst()).quantize(Decimal("0.01"))

    def igst(self):
        if self.tax_type != "IGST":
            return Decimal("0.00")
        return self.tax_amount()

    def total_with_tax(self):
        return (self.subtotal_after_discount() + self.tax_amount()).quantize(
            Decimal("0.01")
        )

    def total_amount(self):
        return self.total_with_tax()

    def total_in_words(self):
        return number_to_words_indian(self.total_amount())

    def get_upi_qr_data_url(self, company):
        if company and company.upi_id:
            ref = self.quote_number or f"Quote-{self.id}"
            return make_upi_qr_data_url(
                company.upi_id, company.name, self.total_amount(), ref
            )
        return ""

    def __str__(self):
        ref = self.quote_number or f"#{self.id}"
        return f"Quotation {ref} for {self.customer.name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override standard price",
    )
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        help_text="GST percentage for this specific line item",
    )
    unit = models.CharField(max_length=20, default="Pcs", blank=True)
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Line item discount",
    )

    @property
    def effective_price(self):
        if self.unit_price is not None:
            return self.unit_price
        return self.item.price if self.item else Decimal("0.00")

    @property
    def total(self):
        line_sub = self.effective_price * self.quantity
        disc = self.discount or Decimal("0.00")
        return max(Decimal("0.00"), line_sub - disc)

    def tax_amount(self):
        gst = self.gst_percent if self.gst_percent is not None else Decimal("0.00")
        return (self.total * (gst / Decimal("100.00"))).quantize(Decimal("0.01"))

    def cgst_percent(self):
        if not self.quotation or self.quotation.tax_type == "IGST":
            return Decimal("0.00")
        return ((self.gst_percent or Decimal("0.00")) / Decimal("2")).quantize(Decimal("0.01"))

    def sgst_percent(self):
        return self.cgst_percent()

    def cgst_amount(self):
        if not self.quotation or self.quotation.tax_type == "IGST":
            return Decimal("0.00")
        return (self.tax_amount() / Decimal("2")).quantize(Decimal("0.01"))

    def sgst_amount(self):
        if not self.quotation or self.quotation.tax_type == "IGST":
            return Decimal("0.00")
        return (self.tax_amount() - self.cgst_amount()).quantize(Decimal("0.01"))

    def igst_amount(self):
        if not self.quotation or self.quotation.tax_type != "IGST":
            return Decimal("0.00")
        return self.tax_amount()

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Unpaid", "Unpaid"),
        ("Partially Paid", "Partially Paid"),
        ("Paid", "Paid"),
        ("Overdue", "Overdue"),
    ]

    TAX_TYPE_CHOICES = [
        ("CGST_SGST", "CGST + SGST (Intra-state)"),
        ("IGST", "IGST (Inter-state)"),
    ]

    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, null=True, blank=True
    )
    invoice_number = models.CharField(
        max_length=50, blank=True, help_text="e.g. INV-0001"
    )
    issued_date = models.DateField(
        default=date.today, help_text="Invoice date (defaults to today)"
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=INVOICE_STATUS_CHOICES, default="Unpaid"
    )
    po_number = models.CharField(
        max_length=50, blank=True, help_text="Purchase Order Number"
    )
    po_date = models.DateField(null=True, blank=True)
    tax_type = models.CharField(
        max_length=20, choices=TAX_TYPE_CHOICES, default="CGST_SGST"
    )
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Fallback global GST percentage",
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.invoice_number:
            self.invoice_number = f"INV-{self.id:04d}"
            super().save(update_fields=["invoice_number"])

    def subtotal(self):
        if (
            self.quotation
            and self.quotation.quotationitem_set.exists()
            and not self.invoiceitem_set.exists()
        ):
            return self.quotation.subtotal_after_discount()
        total = Decimal("0.00")
        for ii in self.invoiceitem_set.all():
            total += ii.total
        disc = self.discount_amount or Decimal("0.00")
        return max(Decimal("0.00"), total - disc)

    def effective_tax_type(self):
        return self.quotation.tax_type if self.quotation else self.tax_type

    def tax_amount(self):
        items = self.invoiceitem_set.all()
        if items.exists():
            return sum((ii.tax_amount() for ii in items), Decimal("0.00")).quantize(Decimal("0.01"))
        if self.quotation and self.quotation.quotationitem_set.exists():
            return self.quotation.tax_amount()
        gst = self.gst_percent
        if not gst:
            return Decimal("0.00")
        return (self.subtotal() * (gst / Decimal("100.00"))).quantize(Decimal("0.01"))

    def cgst(self):
        if self.effective_tax_type() == "IGST":
            return Decimal("0.00")
        items = self.invoiceitem_set.all()
        if items.exists():
            return sum((ii.cgst_amount() for ii in items), Decimal("0.00")).quantize(Decimal("0.01"))
        if self.quotation and self.quotation.quotationitem_set.exists():
            return self.quotation.cgst()
        return (self.tax_amount() / Decimal("2")).quantize(Decimal("0.01"))

    def sgst(self):
        if self.effective_tax_type() == "IGST":
            return Decimal("0.00")
        items = self.invoiceitem_set.all()
        if items.exists():
            return sum((ii.sgst_amount() for ii in items), Decimal("0.00")).quantize(Decimal("0.01"))
        if self.quotation and self.quotation.quotationitem_set.exists():
            return self.quotation.sgst()
        return (self.tax_amount() - self.cgst()).quantize(Decimal("0.01"))

    def igst(self):
        if self.effective_tax_type() != "IGST":
            return Decimal("0.00")
        return self.tax_amount()

    def total_amount(self):
        return (self.subtotal() + self.tax_amount()).quantize(Decimal("0.01"))

    def total_in_words(self):
        return number_to_words_indian(self.total_amount())

    def paid_amount(self):
        total = Decimal("0.00")
        for receipt in self.paymentreceipt_set.all():
            total += receipt.amount_paid
        return total.quantize(Decimal("0.01"))

    def balance_due(self):
        bal = self.total_amount() - self.paid_amount()
        return max(Decimal("0.00"), bal).quantize(Decimal("0.01"))

    def get_upi_qr_data_url(self, company):
        if company and company.upi_id:
            ref = self.invoice_number or f"Inv-{self.id}"
            bal = self.balance_due() if self.paid_amount() > 0 else self.total_amount()
            return make_upi_qr_data_url(company.upi_id, company.name, bal, ref)
        return ""

    def update_payment_status(self):
        paid = self.paid_amount()
        total = self.total_amount()
        if paid >= total and total > 0:
            self.status = "Paid"
        elif paid > 0:
            self.status = "Partially Paid"
        self.save(update_fields=["status"])

    def __str__(self):
        ref = self.invoice_number or f"#{self.id}"
        if self.quotation:
            return f"Invoice {ref} (from Quote {self.quotation.quote_number or self.quotation.id})"
        return f"Invoice {ref}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        help_text="GST percentage for this specific line item",
    )
    unit = models.CharField(max_length=20, default="Pcs", blank=True)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    @property
    def effective_price(self):
        if self.unit_price is not None:
            return self.unit_price
        return self.item.price if self.item else Decimal("0.00")

    @property
    def total(self):
        line_sub = self.effective_price * self.quantity
        disc = self.discount or Decimal("0.00")
        return max(Decimal("0.00"), line_sub - disc)

    def tax_amount(self):
        gst = self.gst_percent if self.gst_percent is not None else Decimal("0.00")
        return (self.total * (gst / Decimal("100.00"))).quantize(Decimal("0.01"))

    def cgst_percent(self):
        tax_type = self.invoice.effective_tax_type() if self.invoice else "CGST_SGST"
        if tax_type == "IGST":
            return Decimal("0.00")
        return ((self.gst_percent or Decimal("0.00")) / Decimal("2")).quantize(Decimal("0.01"))

    def sgst_percent(self):
        return self.cgst_percent()

    def cgst_amount(self):
        tax_type = self.invoice.effective_tax_type() if self.invoice else "CGST_SGST"
        if tax_type == "IGST":
            return Decimal("0.00")
        return (self.tax_amount() / Decimal("2")).quantize(Decimal("0.01"))

    def sgst_amount(self):
        tax_type = self.invoice.effective_tax_type() if self.invoice else "CGST_SGST"
        if tax_type == "IGST":
            return Decimal("0.00")
        return (self.tax_amount() - self.cgst_amount()).quantize(Decimal("0.01"))

    def igst_amount(self):
        tax_type = self.invoice.effective_tax_type() if self.invoice else "CGST_SGST"
        if tax_type != "IGST":
            return Decimal("0.00")
        return self.tax_amount()

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class PaymentReceipt(models.Model):
    PAYMENT_MODE_CHOICES = [
        ("UPI", "UPI / GPay / PhonePe"),
        ("Bank Transfer", "Bank Transfer (NEFT/IMPS/RTGS)"),
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
        ("Card", "Credit / Debit Card"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_date = models.DateField(default=date.today)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(
        max_length=30, choices=PAYMENT_MODE_CHOICES, default="UPI"
    )
    reference_no = models.CharField(
        max_length=100, blank=True, help_text="UTR / Transaction ID / Cheque No"
    )
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.invoice:
            self.invoice.update_payment_status()

    def __str__(self):
        return f"Payment ₹{self.amount_paid} for {self.invoice}"


class CompanyInfo(models.Model):
    THEME_CHOICES = [
        ("navy", "Classic Navy Blue"),
        ("emerald", "Emerald Green"),
        ("indigo", "Royal Indigo"),
        ("charcoal", "Corporate Charcoal"),
    ]

    name = models.CharField(max_length=255)
    gst_no = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    account_details = models.TextField(blank=True)
    owner_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    business_category = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
        help_text="Upload logo photo from system",
    )
    logo_url = models.CharField(
        max_length=500, blank=True, help_text="Fallback image URL for logo"
    )
    signature = models.ImageField(
        upload_to="company_signatures/",
        blank=True,
        null=True,
        help_text="Upload digital signature / stamp photo",
    )
    theme_color = models.CharField(
        max_length=20, choices=THEME_CHOICES, default="navy"
    )
    bank_name = models.CharField(max_length=100, blank=True)
    account_no = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=50, blank=True)
    signatory_title = models.CharField(
        max_length=100, default="Authorized Signatory", blank=True
    )

    def __str__(self):
        return self.name
