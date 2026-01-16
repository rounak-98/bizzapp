from django.contrib import admin

from .models import Customer, Invoice, Item, Quotation, QuotationItem

admin.site.register(Customer)
admin.site.register(Item)
admin.site.register(Quotation)
admin.site.register(QuotationItem)
admin.site.register(Invoice)
