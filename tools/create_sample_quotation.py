#!/usr/bin/env python
import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bizapp.settings')
import django
import sys
from pathlib import Path
# ensure project root on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# ensure DB env (MySQL) if available — adjust as needed
os.environ.setdefault('DB_ENGINE', 'django.db.backends.mysql')
os.environ.setdefault('DB_NAME', 'bizzapp')
os.environ.setdefault('DB_USER', 'root')
os.environ.setdefault('DB_PASSWORD', 'Rounak@8789')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '3306')

django.setup()
from core.models import Customer, Item, Quotation, QuotationItem

cust, _ = Customer.objects.get_or_create(name='Demo Customer', defaults={'email':'demo@example.com','phone':'000'})
item, _ = Item.objects.get_or_create(name='Demo Item', defaults={'description':'Demo','quantity':100,'price':Decimal('100.00')})

# create a quotation only if none with this customer exists
q = Quotation.objects.create(customer=cust, gst_percent=18)
QuotationItem.objects.create(quotation=q, item=item, quantity=2)
print('CREATED_QUOTATION_ID=' + str(q.id))
