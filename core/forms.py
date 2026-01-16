from django import forms
from django.forms import inlineformset_factory


class ForceSelectMixin:
    """Mixin to add a CSS class to all Select widgets so we can style them reliably."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.forms.widgets import Select

        for name, field in self.fields.items():
            if isinstance(field.widget, Select):
                existing = field.widget.attrs.get("class", "")
                classes = (existing + " force-select").strip()
                field.widget.attrs["class"] = classes

from .models import CompanyInfo, Customer, Invoice, InvoiceItem, Item, Quotation, QuotationItem, Term


class CustomerForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "address", "business_category", "shopping_details"]


class ItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "quantity", "price"]


class QuotationForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ["customer", "terms", "gst_percent"]  # exclude 'date' (auto_now_add)


class QuotationItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["quotation", "item", "quantity"]


from django.forms import inlineformset_factory

QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    extra=1,  # show 1 item row by default; allow adding more dynamically
    can_delete=False,
)


class InvoiceForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["quotation"]  # exclude 'issued_date' (auto_now_add)


class InvoiceCreateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["quotation", "gst_percent"]

class InvoiceItemForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["item", "quantity"]


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=3,
    can_delete=False,
)


class TermForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = Term
        fields = ["title", "content"]


class CompanyInfoForm(ForceSelectMixin, forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ["name", "owner_name", "gst_no", "email", "address", "business_category", "account_details"]


class PerformaForm(forms.Form):
    amount_paid = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, initial=0
    )
    paid_on = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":2}))
