from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Manage
    path("company/", views.company_info, name="company_info"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.create_customer, name="create_customer"),
    path("customers/<int:pk>/statement/", views.customer_statement, name="customer_statement"),
    path("items/", views.item_list, name="item_list"),
    path("items/add/", views.create_item, name="create_item"),
    path("terms/", views.term_list, name="term_list"),
    path("terms/add/", views.create_term, name="create_term"),
    path("terms/<int:pk>/edit/", views.edit_term, name="edit_term"),
    path("terms/<int:pk>/delete/", views.delete_term, name="delete_term"),
    # Quotations & Performas
    path("quotations/", views.quotation_list, name="quotation_list"),
    path("quotations/create/", views.create_quotation, name="create_quotation"),
    path("quotations/<int:pk>/edit/", views.edit_quotation, name="edit_quotation"),
    path("quotations/<int:pk>/", views.quotation_detail, name="quotation_detail"),
    path("quotations/<int:pk>/pdf/", views.quotation_pdf, name="quotation_pdf"),
    path("quotations/<int:pk>/convert/", views.convert_quotation, name="convert_quotation"),
    path("quotations/<int:pk>/status/", views.update_quotation_status, name="update_quotation_status"),
    path("quotations/<int:pk>/performa/", views.performa_invoice, name="performa_invoice"),
    path("quotations/<int:pk>/performa/create/", views.create_performa, name="performa_create"),
    path("performas/", views.performa_list, name="performa_list"),
    # Invoices & Payments
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/create/", views.create_invoice, name="create_invoice"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("invoices/<int:pk>/status/", views.update_invoice_status, name="update_invoice_status"),
    path("invoices/<int:pk>/pay/", views.add_payment_receipt, name="add_payment_receipt"),
    path("revenue/", views.revenue, name="revenue"),
]
