from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import DateInput, FileInput, Select, Textarea

from .models import CompanyInfo, Customer, Invoice, InvoiceItem, Item, PaymentReceipt, Quotation, QuotationItem, Term


class ForceSelectMixin:
    """Mixin to add a CSS class to widgets so we can style them reliably."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, Select):
                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (existing + " force-select").strip()


class CustomerForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "gstin", "address", "business_category", "shopping_details"]


class ItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "hsn_code", "description", "quantity", "price", "gst_percent"]
        widgets = {
            "hsn_code": forms.TextInput(attrs={"placeholder": "e.g. 8471 or 9983"}),
            "gst_percent": forms.NumberInput(attrs={"placeholder": "18", "step": "0.01"}),
        }


class QuotationForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            "customer",
            "quote_number",
            "date",
            "status",
            "valid_until",
            "po_number",
            "po_date",
            "tax_type",
            "discount_amount",
            "terms",
            "notes",
        ]
        widgets = {
            "date": DateInput(attrs={"type": "date"}),
            "valid_until": DateInput(attrs={"type": "date"}),
            "po_date": DateInput(attrs={"type": "date"}),
            "notes": Textarea(attrs={"rows": 2}),
        }


class QuotationItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["item", "quantity", "unit_price", "gst_percent", "unit", "discount"]
        widgets = {
            "unit_price": forms.NumberInput(attrs={"placeholder": "Default", "step": "0.01"}),
            "gst_percent": forms.NumberInput(attrs={"placeholder": "GST %", "step": "0.01"}),
            "discount": forms.NumberInput(attrs={"step": "0.01"}),
            "unit": forms.TextInput(attrs={"placeholder": "Pcs/Hrs/Sets"}),
        }


QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    extra=1,
    can_delete=True,
)


class InvoiceForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "quotation",
            "invoice_number",
            "issued_date",
            "status",
            "due_date",
            "po_number",
            "po_date",
            "tax_type",
            "discount_amount",
            "notes",
        ]
        widgets = {
            "issued_date": DateInput(attrs={"type": "date"}),
            "due_date": DateInput(attrs={"type": "date"}),
            "po_date": DateInput(attrs={"type": "date"}),
            "notes": Textarea(attrs={"rows": 2}),
        }


class InvoiceCreateForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "quotation",
            "invoice_number",
            "issued_date",
            "status",
            "due_date",
            "po_number",
            "po_date",
            "tax_type",
            "discount_amount",
            "notes",
        ]
        widgets = {
            "issued_date": DateInput(attrs={"type": "date"}),
            "due_date": DateInput(attrs={"type": "date"}),
            "po_date": DateInput(attrs={"type": "date"}),
            "notes": Textarea(attrs={"rows": 2}),
        }


class InvoiceItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["item", "quantity", "unit_price", "gst_percent", "unit", "discount"]
        widgets = {
            "unit_price": forms.NumberInput(attrs={"placeholder": "Default", "step": "0.01"}),
            "gst_percent": forms.NumberInput(attrs={"placeholder": "GST %", "step": "0.01"}),
            "discount": forms.NumberInput(attrs={"step": "0.01"}),
            "unit": forms.TextInput(attrs={"placeholder": "Pcs/Hrs/Sets"}),
        }


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
)


class PaymentReceiptForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = PaymentReceipt
        fields = ["payment_date", "amount_paid", "payment_mode", "reference_no", "notes"]
        widgets = {
            "payment_date": DateInput(attrs={"type": "date"}),
            "notes": Textarea(attrs={"rows": 2}),
            "reference_no": forms.TextInput(attrs={"placeholder": "UTR / Transaction Ref"}),
        }


class TermForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Term
        fields = ["title", "content"]


class CompanyInfoForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = [
            "name",
            "owner_name",
            "gst_no",
            "email",
            "phone",
            "address",
            "business_category",
            "logo",
            "logo_url",
            "signature",
            "theme_color",
            "bank_name",
            "account_no",
            "ifsc_code",
            "upi_id",
            "account_details",
            "signatory_title",
        ]
        widgets = {
            "account_details": Textarea(attrs={"rows": 3}),
            "logo": FileInput(attrs={"accept": "image/*"}),
            "signature": FileInput(attrs={"accept": "image/*"}),
            "logo_url": forms.TextInput(attrs={"placeholder": "https://example.com/logo.png"}),
        }


class PerformaForm(forms.Form):
    amount_paid = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, initial=0
    )
    paid_on = forms.DateField(required=False, widget=DateInput(attrs={"type": "date"}))
    note = forms.CharField(required=False, widget=Textarea(attrs={"rows": 2}))
