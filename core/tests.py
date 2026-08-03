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
        self.quotation = Quotation.objects.create(customer=self.customer, gst_percent=Decimal("18.00"))
        QuotationItem.objects.create(
            quotation=self.quotation, item=self.item1, quantity=2
        )
        QuotationItem.objects.create(
            quotation=self.quotation, item=self.item2, quantity=3
        )
        self.invoice = Invoice.objects.create(quotation=self.quotation)

    def test_quotation_subtotal_and_totals(self):
        # 2 * 99.99 + 3 * 10.00 = 199.98 + 30.00 = 229.98
        self.assertEqual(self.quotation.subtotal(), Decimal("229.98"))
        # tax @ 18% = 229.98 * 0.18 = 41.3964 -> 41.40
        self.assertEqual(self.quotation.tax_amount(), Decimal("41.40"))
        # total with tax = 229.98 + 41.40 = 271.38
        self.assertEqual(self.quotation.total_amount(), Decimal("271.38"))

    def test_invoice_total_amount(self):
        self.assertEqual(self.invoice.total_amount(), self.quotation.total_amount())

    def test_quote_number_auto_generation(self):
        self.assertTrue(self.quotation.quote_number.startswith("QTN-"))

    def test_custom_line_price_and_discount(self):
        q = Quotation.objects.create(customer=self.customer, discount_amount=Decimal("10.00"))
        QuotationItem.objects.create(
            quotation=q, item=self.item1, quantity=1, unit_price=Decimal("100.00"), discount=Decimal("5.00")
        )
        # Line total = 100 * 1 - 5 = 95.00
        # Quote subtotal after disc = 95 - 10 = 85.00
        self.assertEqual(q.subtotal(), Decimal("95.00"))
        self.assertEqual(q.subtotal_after_discount(), Decimal("85.00"))

    def test_line_item_description_and_editing(self):
        q = Quotation.objects.create(customer=self.customer)
        qi = QuotationItem.objects.create(
            quotation=q,
            item=self.item1,
            quantity=1,
            description="Rented for 15 days",
        )
        self.assertEqual(qi.description, "Rented for 15 days")

        # Test edit item view
        response = self.client.post(
            f"/items/{self.item1.id}/edit/",
            {
                "name": "Updated Widget",
                "hsn_code": "8471",
                "description": "Premium Widget",
                "quantity": 20,
                "price": "149.99",
                "gst_percent": "18.00",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.name, "Updated Widget")
        self.assertEqual(self.item1.price, Decimal("149.99"))
