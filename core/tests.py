from decimal import Decimal

from django.test import TestCase

from core.models import Customer, Invoice, Item, Quotation, QuotationItem


class TotalsTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Co")
        self.item1 = Item.objects.create(
            name="Widget", quantity=10, price=Decimal("99.99")
        )
        self.item2 = Item.objects.create(
            name="Gadget", quantity=5, price=Decimal("10.00")
        )
        self.quotation = Quotation.objects.create(customer=self.customer)
        QuotationItem.objects.create(
            quotation=self.quotation, item=self.item1, quantity=2
        )
        QuotationItem.objects.create(
            quotation=self.quotation, item=self.item2, quantity=3
        )
        self.invoice = Invoice.objects.create(quotation=self.quotation)

    def test_quotation_total_amount(self):
        # 2 * 99.99 + 3 * 10.00 = 199.98 + 30.00 = 229.98
        expected = Decimal("229.98")
        self.assertEqual(self.quotation.total_amount(), expected)

    def test_invoice_total_amount(self):
        self.assertEqual(self.invoice.total_amount(), self.quotation.total_amount())
