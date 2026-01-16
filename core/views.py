from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal

from .forms import (
    CompanyInfoForm,
    CustomerForm,
    InvoiceForm,
    InvoiceCreateForm,
    InvoiceItemForm,
    InvoiceItemFormSet,
    ItemForm,
    QuotationForm,
    QuotationItemForm,
    QuotationItemFormSet,
    TermForm,
)
from .models import (
    CompanyInfo,
    Customer,
    Invoice,
    InvoiceItem,
    Item,
    Quotation,
    QuotationItem,
    Term,
)


# Homepage view
def dashboard(request):
    # include recent quotations to allow quick performa creation from dashboard
    quotations = Quotation.objects.all().order_by("-date")[:10]
    return render(request, "dashboard.html", {"quotations": quotations})


# List views
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"customers": customers})


def item_list(request):
    items = Item.objects.all()
    return render(request, "item_list.html", {"items": items})


def quotation_list(request):
    quotations = Quotation.objects.all()
    return render(request, "quotation_list.html", {"quotations": quotations})


def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, "invoice_list.html", {"invoices": invoices})


def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "create_customer.html", {"form": form})


def create_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("item_list")
    else:
        form = ItemForm()
    return render(request, "create_item.html", {"form": form})


def create_invoice(request):
    # Support creating invoices from an existing quotation or directly with items
    if request.method == "POST":
        form = InvoiceCreateForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoice_list")
    else:
        form = InvoiceCreateForm()
        formset = InvoiceItemFormSet()
    return render(request, "create_invoice.html", {"form": form, "formset": formset})


def edit_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        form = QuotationForm(request.POST, instance=quotation)
        formset = QuotationItemFormSet(request.POST, instance=quotation)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("quotation_detail", pk=quotation.pk)
    else:
        form = QuotationForm(instance=quotation)
        formset = QuotationItemFormSet(instance=quotation)
    return render(request, "create_quotation.html", {"form": form, "formset": formset, "editing": True})


def performa_list(request):
    quotations = Quotation.objects.all()
    return render(request, "performa_list.html", {"quotations": quotations})


def company_info(request):
    company = CompanyInfo.objects.first()
    if request.method == "POST":
        form = CompanyInfoForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_info")
    else:
        form = CompanyInfoForm(instance=company)
    return render(request, "company_info.html", {"form": form})


def create_quotation(request):
    if request.method == "POST":
        form = QuotationForm(request.POST)
        formset = QuotationItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            quotation = form.save()
            formset.instance = quotation
            formset.save()
            return redirect("quotation_detail", pk=quotation.pk)
    else:
        form = QuotationForm()
        formset = QuotationItemFormSet()
    return render(request, "create_quotation.html", {"form": form, "formset": formset})


def term_list(request):
    terms = Term.objects.all()
    return render(request, "term_list.html", {"terms": terms})


def create_term(request):
    if request.method == "POST":
        form = TermForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("term_list")
    else:
        form = TermForm()
    return render(request, "create_term.html", {"form": form})


def revenue(request):
    invoices = Invoice.objects.all()
    total_revenue = sum(invoice.total_amount() for invoice in invoices)
    return render(
        request, "revenue.html", {"invoices": invoices, "total_revenue": total_revenue}
    )


def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    return render(
        request,
        "quotation_details.html",
        {"quotation": quotation, "items": items, "company": company},
    )


def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)
    company = CompanyInfo.objects.first()
    return render(
        request,
        "invoice_detail.html",
        {"invoice": invoice, "items": items, "company": company},
    )


def performa_invoice(request, pk):
    """Render a printable performa invoice for the given quotation (no DB write)."""
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    return render(
        request,
        "performa_invoice.html",
        {"quotation": quotation, "items": items, "company": company},
    )


def create_performa(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    from .forms import PerformaForm

    if request.method == "POST":
        form = PerformaForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data.get("amount_paid") or 0
            paid_on = form.cleaned_data.get("paid_on")
            note = form.cleaned_data.get("note")
            total = quotation.total_with_tax()
            remaining = (total - Decimal(amount_paid)).quantize(Decimal("0.01"))
            items = quotation.quotationitem_set.all()
            company = CompanyInfo.objects.first()
            return render(
                request,
                "performa_invoice.html",
                {
                    "quotation": quotation,
                    "items": items,
                    "company": company,
                    "amount_paid": amount_paid,
                    "paid_on": paid_on,
                    "note": note,
                    "remaining": remaining,
                },
            )
    else:
        form = PerformaForm()

    return render(request, "performa_create.html", {"form": form, "quotation": quotation})
