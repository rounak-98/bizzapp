import json
from decimal import Decimal
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from xhtml2pdf import pisa

from .forms import (
    CompanyInfoForm,
    CustomerForm,
    InvoiceCreateForm,
    InvoiceForm,
    InvoiceItemFormSet,
    ItemForm,
    PaymentReceiptForm,
    PerformaForm,
    QuotationForm,
    QuotationItemFormSet,
    TermForm,
)
from .models import (
    CompanyInfo,
    Customer,
    Invoice,
    InvoiceItem,
    Item,
    PaymentReceipt,
    Quotation,
    QuotationItem,
    Term,
)


def dashboard(request):
    quotations = Quotation.objects.all().order_by("-id")
    invoices = Invoice.objects.all().order_by("-id")

    accepted_quotes = quotations.filter(status="Accepted")
    pending_quotes = quotations.filter(status__in=["Draft", "Sent"])
    converted_quotes = quotations.filter(status="Converted")

    accepted_value = sum(q.total_amount() for q in accepted_quotes)
    total_invoiced_value = sum(i.total_amount() for i in invoices)

    context = {
        "recent_quotations": quotations[:10],
        "recent_invoices": invoices[:5],
        "total_quotes_count": quotations.count(),
        "accepted_quotes_count": accepted_quotes.count(),
        "accepted_value": accepted_value,
        "pending_quotes_count": pending_quotes.count(),
        "converted_quotes_count": converted_quotes.count(),
        "total_invoiced_value": total_invoiced_value,
        "total_customers_count": Customer.objects.count(),
        "total_items_count": Item.objects.count(),
    }
    return render(request, "dashboard.html", context)


def customer_list(request):
    query = request.GET.get("q", "").strip()
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(
            models.Q(name__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(phone__icontains=query)
            | models.Q(gstin__icontains=query)
        )
    return render(request, "customer_list.html", {"customers": customers, "query": query})


def customer_statement(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    company = CompanyInfo.objects.first()
    invoices = Invoice.objects.filter(quotation__customer=customer).order_by("issued_date")
    payments = PaymentReceipt.objects.filter(invoice__quotation__customer=customer).order_by("payment_date")

    return render(
        request,
        "customer_statement.html",
        {
            "customer": customer,
            "company": company,
            "invoices": invoices,
            "payments": payments,
        },
    )


def item_list(request):
    query = request.GET.get("q", "").strip()
    items = Item.objects.all()
    if query:
        items = items.filter(
            models.Q(name__icontains=query)
            | models.Q(description__icontains=query)
            | models.Q(hsn_code__icontains=query)
        )
    return render(request, "item_list.html", {"items": items, "query": query})


def quotation_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    quotations = Quotation.objects.all().order_by("-id")
    if query:
        quotations = quotations.filter(
            models.Q(quote_number__icontains=query)
            | models.Q(customer__name__icontains=query)
        )
    if status_filter:
        quotations = quotations.filter(status=status_filter)

    return render(
        request,
        "quotation_list.html",
        {
            "quotations": quotations,
            "query": query,
            "status_filter": status_filter,
            "status_choices": Quotation.STATUS_CHOICES,
        },
    )


def invoice_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    invoices = Invoice.objects.all().order_by("-id")
    if query:
        invoices = invoices.filter(
            models.Q(invoice_number__icontains=query)
            | models.Q(quotation__customer__name__icontains=query)
        )
    if status_filter:
        invoices = invoices.filter(status=status_filter)

    return render(
        request,
        "invoice_list.html",
        {
            "invoices": invoices,
            "query": query,
            "status_filter": status_filter,
            "status_choices": Invoice.INVOICE_STATUS_CHOICES,
        },
    )


def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "create_customer.html", {"form": form})


def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "create_customer.html", {"form": form, "editing": True, "customer": customer})


def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("customer_list")
    return render(request, "delete_customer_confirm.html", {"customer": customer})


def create_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("item_list")
    else:
        form = ItemForm()
    return render(request, "create_item.html", {"form": form})


def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("item_list")
    else:
        form = ItemForm(instance=item)
    return render(request, "create_item.html", {"form": form, "editing": True, "item": item})


def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect("item_list")
    return render(request, "delete_item_confirm.html", {"item": item})


def create_quotation(request):
    terms_dict = {str(t.id): t.content for t in Term.objects.all()}
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
    return render(
        request,
        "create_quotation.html",
        {"form": form, "formset": formset, "terms_json": json.dumps(terms_dict)},
    )


def edit_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    terms_dict = {str(t.id): t.content for t in Term.objects.all()}
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
    return render(
        request,
        "create_quotation.html",
        {
            "form": form,
            "formset": formset,
            "editing": True,
            "quotation": quotation,
            "terms_json": json.dumps(terms_dict),
        },
    )


def convert_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    invoice = Invoice.objects.filter(quotation=quotation).first()
    if not invoice:
        invoice = Invoice.objects.create(
            customer=quotation.customer,
            quotation=quotation,
            gst_percent=quotation.gst_percent,
            discount_amount=quotation.discount_amount,
            notes=quotation.notes,
            status="Unpaid",
        )
        for q_item in quotation.quotationitem_set.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                item=q_item.item,
                description=q_item.description,
                quantity=q_item.quantity,
                unit_price=q_item.unit_price,
                gst_percent=q_item.gst_percent,
                unit=q_item.unit,
                discount=q_item.discount,
            )
    quotation.status = "Converted"
    quotation.save(update_fields=["status"])
    return redirect("invoice_detail", pk=invoice.pk)


def update_quotation_status(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Quotation.STATUS_CHOICES):
            quotation.status = new_status
            quotation.save(update_fields=["status"])
    return redirect("quotation_detail", pk=quotation.pk)


def update_invoice_status(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Invoice.INVOICE_STATUS_CHOICES):
            invoice.status = new_status
            invoice.save(update_fields=["status"])
    return redirect("invoice_detail", pk=invoice.pk)


def add_payment_receipt(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        form = PaymentReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.invoice = invoice
            receipt.save()
            return redirect("invoice_detail", pk=invoice.pk)
    return redirect("invoice_detail", pk=invoice.pk)


def create_invoice(request):
    if request.method == "POST":
        form = InvoiceCreateForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceCreateForm()
        formset = InvoiceItemFormSet()
    return render(request, "create_invoice.html", {"form": form, "formset": formset})


def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    return render(
        request,
        "create_invoice.html",
        {"form": form, "formset": formset, "editing": True, "invoice": invoice},
    )


def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice.delete()
        return redirect("invoice_list")
    return render(request, "delete_invoice_confirm.html", {"invoice": invoice})


def delete_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        quotation.delete()
        return redirect("quotation_list")
    return render(request, "delete_quotation_confirm.html", {"quotation": quotation})


def performa_list(request):
    quotations = Quotation.objects.all().order_by("-id")
    return render(request, "performa_list.html", {"quotations": quotations})


def company_info(request):
    company = CompanyInfo.objects.first()
    if request.method == "POST":
        form = CompanyInfoForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_info")
    else:
        form = CompanyInfoForm(instance=company)
    return render(request, "company_info.html", {"form": form, "company": company})


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


def edit_term(request, pk):
    term = get_object_or_404(Term, pk=pk)
    if request.method == "POST":
        form = TermForm(request.POST, instance=term)
        if form.is_valid():
            form.save()
            return redirect("term_list")
    else:
        form = TermForm(instance=term)
    return render(request, "create_term.html", {"form": form, "editing": True, "term": term})


def delete_term(request, pk):
    term = get_object_or_404(Term, pk=pk)
    if request.method == "POST":
        term.delete()
        return redirect("term_list")
    return render(request, "delete_term_confirm.html", {"term": term})


def revenue(request):
    invoices = Invoice.objects.all()
    total_revenue = sum(invoice.total_amount() for invoice in invoices)
    paid_revenue = sum(invoice.paid_amount() for invoice in invoices)
    unpaid_revenue = sum(invoice.balance_due() for invoice in invoices)
    return render(
        request,
        "revenue.html",
        {
            "invoices": invoices,
            "total_revenue": total_revenue,
            "paid_revenue": paid_revenue,
            "unpaid_revenue": unpaid_revenue,
        },
    )


def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    upi_qr_url = quotation.get_upi_qr_data_url(company)

    return render(
        request,
        "quotation_details.html",
        {
            "quotation": quotation,
            "items": items,
            "company": company,
            "upi_qr_url": upi_qr_url,
            "status_choices": Quotation.STATUS_CHOICES,
        },
    )


def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)
    if not items.exists() and invoice.quotation:
        items = invoice.quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    upi_qr_url = invoice.get_upi_qr_data_url(company)
    payment_form = PaymentReceiptForm()
    payments = invoice.paymentreceipt_set.all().order_by("-payment_date")

    return render(
        request,
        "invoice_detail.html",
        {
            "invoice": invoice,
            "items": items,
            "company": company,
            "upi_qr_url": upi_qr_url,
            "payment_form": payment_form,
            "payments": payments,
            "status_choices": Invoice.INVOICE_STATUS_CHOICES,
        },
    )


def performa_invoice(request, pk):
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
    if request.method == "POST":
        form = PerformaForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data.get("amount_paid") or 0
            paid_on = form.cleaned_data.get("paid_on")
            note = form.cleaned_data.get("note")
            total = quotation.total_amount()
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


def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, uri.lstrip("/"))
    else:
        path = uri
    if not os.path.isfile(path):
        return uri
    return path


def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    template = get_template("quotation_details.html")
    context = {"quotation": quotation, "items": items, "company": company, "is_pdf": True}
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Quotation_{quotation.quote_number or quotation.id}.pdf"'
    )
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)
    if not items.exists() and invoice.quotation:
        items = invoice.quotation.quotationitem_set.all()
    company = CompanyInfo.objects.first()
    template = get_template("invoice_detail.html")
    context = {"invoice": invoice, "items": items, "company": company, "is_pdf": True}
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Invoice_{invoice.invoice_number or invoice.id}.pdf"'
    )
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response
