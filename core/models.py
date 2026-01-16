from decimal import Decimal

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    business_category = models.CharField(max_length=100, blank=True)
    shopping_details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Term(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class Quotation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    items = models.ManyToManyField(Item, through="QuotationItem")
    terms = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    gst_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="GST percentage (e.g. 18 for 18%)"
    )

    def subtotal(self):
        total = Decimal("0.00")
        for qi in self.quotationitem_set.all():
            total += qi.item.price * qi.quantity
        return total

    def tax_amount(self):
        if not self.gst_percent:
            return Decimal("0.00")
        return (self.subtotal() * (self.gst_percent / Decimal("100.00"))).quantize(Decimal("0.01"))

    def cgst_percent(self):
        if not self.gst_percent:
            return Decimal("0.00")
        return (self.gst_percent / Decimal("2")).quantize(Decimal("0.01"))

    def sgst_percent(self):
        return self.cgst_percent()

    def cgst(self):
        """Compute CGST as subtotal * (gst_percent/2) / 100 with rounding."""
        if not self.gst_percent:
            return Decimal("0.00")
        cgst_pct = self.gst_percent / Decimal("2")
        cgst_amt = (self.subtotal() * (cgst_pct / Decimal("100"))).quantize(Decimal("0.01"))
        return cgst_amt

    def sgst(self):
        """Compute SGST so that CGST + SGST == tax_amount() after rounding."""
        if not self.gst_percent:
            return Decimal("0.00")
        # calculate sgst as the remainder to ensure sums match the total tax_amount
        sgst_amt = (self.tax_amount() - self.cgst()).quantize(Decimal("0.01"))
        return sgst_amt

    def total_with_tax(self):
        return (self.subtotal() + self.tax_amount()).quantize(Decimal("0.01"))

    def __str__(self):
        return f"Quotation #{self.id} for {self.customer.name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def total(self):
        return self.quantity * self.item.price

    def cgst_amount(self):
        """CGST amount for this line (half of GST percent applied to line total)."""
        if not self.quotation or not self.quotation.gst_percent:
            return Decimal("0.00")
        gst_pct = self.quotation.gst_percent / Decimal("100")
        cgst = (self.total * gst_pct / Decimal("2")).quantize(Decimal("0.01"))
        return cgst

    def sgst_amount(self):
        """SGST amount for this line (half of GST percent applied to line total)."""
        if not self.quotation or not self.quotation.gst_percent:
            return Decimal("0.00")
        gst_pct = self.quotation.gst_percent / Decimal("100")
        sgst = (self.total * gst_pct / Decimal("2")).quantize(Decimal("0.01"))
        return sgst

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


from decimal import Decimal

class Invoice(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, null=True, blank=True)
    issued_date = models.DateField(auto_now_add=True)
    gst_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="GST percentage (e.g. 18 for 18%)"
    )

    def total_amount(self):
        if self.quotation:
            return self.quotation.total_with_tax()

        total = Decimal("0.00")
        for ii in self.invoiceitem_set.all():
            total += ii.total

        tax = (total * (self.gst_percent / Decimal("100.00"))).quantize(Decimal("0.01"))
        return (total + tax).quantize(Decimal("0.01"))

    def cgst(self):
        if not self.gst_percent:
            return Decimal("0.00")
        subtotal = sum(ii.total for ii in self.invoiceitem_set.all())
        return (subtotal * (self.gst_percent / Decimal("200.00"))).quantize(Decimal("0.01"))

    def sgst(self):
        return self.cgst()  # symmetrical split

    def __str__(self):
        if self.quotation:
            return f"Invoice #{self.id} for Quotation #{self.quotation.id}"
        return f"Invoice #{self.id} (standalone)"

class CompanyInfo(models.Model):
    name = models.CharField(max_length=255)
    gst_no = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    account_details = models.TextField(blank=True)
    owner_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    business_category = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class InvoiceItem(models.Model):
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
    
    @property
    def total(self):
        return self.quantity * self.item.price

    def cgst_amount(self):
        """CGST for this invoice line. Use quotation GST if available, otherwise invoice GST."""
        gst_pct = None
        if self.invoice:
            if self.invoice.quotation and self.invoice.quotation.gst_percent:
                gst_pct = self.invoice.quotation.gst_percent
            elif self.invoice.gst_percent:
                gst_pct = self.invoice.gst_percent

        if gst_pct:
            return (self.total * (gst_pct / Decimal("100")) / 2).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def sgst_amount(self):
        """SGST for this invoice line. Mirrors CGST calculation."""
        return self.cgst_amount()
