"""
One-time demo seed so every super-admin/admin dashboard shows sample data.
Runs automatically on deploy (migrate-on-startup) against whatever DB is
configured (TiDB in prod). Idempotent via get_or_create; each block is wrapped
so a single failure never breaks the deploy.
"""
from decimal import Decimal
from datetime import date

from django.db import migrations


def seed(apps, schema_editor):
    def safe(fn):
        try:
            fn()
        except Exception as exc:  # pragma: no cover - best-effort seeding
            print(f'[seed_demo] skipped: {exc}')

    Company = apps.get_model('companies', 'Company')
    Building = apps.get_model('workspace', 'Building')
    Floor = apps.get_model('workspace', 'Floor')
    Facility = apps.get_model('facilities', 'Facility')
    InventoryItem = apps.get_model('inventory', 'InventoryItem')
    Vendor = apps.get_model('vendors', 'Vendor')
    VendorBill = apps.get_model('vendors', 'VendorBill')
    Lease = apps.get_model('leases', 'Lease')

    state = {}

    def _company():
        state['company'] = Company.objects.get_or_create(
            slug='acme-corp',
            defaults=dict(name='Acme Corp', email='contact@acmecorp.com', phone='9999999999',
                          address='123 Demo Street', city='Bengaluru', state='Karnataka',
                          pincode='560001', status='active'),
        )[0]

    def _building():
        state['building'] = Building.objects.get_or_create(
            name='Demo Tower',
            defaults=dict(address='123 Demo Street', city='Bengaluru', state='Karnataka', pincode='560001'),
        )[0]

    def _floor():
        state['floor'] = Floor.objects.get_or_create(
            building=state['building'], floor_number=1, defaults=dict(name='1st Floor'),
        )[0]

    def _facility():
        Facility.objects.get_or_create(
            name='Conference Room A', building=state['building'],
            defaults=dict(facility_type='conference_room', floor=state.get('floor'), capacity=12,
                          price_per_hour=Decimal('500'), price_per_day=Decimal('3000'),
                          description='Demo conference room.', is_public=True),
        )

    def _inventory():
        InventoryItem.objects.get_or_create(
            name='Water Bottle 1L', building=state['building'],
            defaults=dict(category='water', unit='pcs', quantity=Decimal('48'),
                          reorder_level=Decimal('10'), unit_cost=Decimal('20')),
        )

    def _vendor():
        state['vendor'] = Vendor.objects.get_or_create(
            name='City Internet', defaults=dict(category='internet', building=state['building'],
                                                contact_person='Support', phone='1800000000'),
        )[0]

    def _vendor_bill():
        VendorBill.objects.get_or_create(
            bill_number='INET-0001', vendor=state['vendor'],
            defaults=dict(building=state['building'], bill_date=date(2026, 6, 1),
                          amount=Decimal('5000'), tax_amount=Decimal('900'),
                          total_amount=Decimal('5900'), status='pending',
                          description='Monthly internet'),
        )

    def _lease():
        Lease.objects.get_or_create(
            company=state['company'], building=state['building'],
            defaults=dict(floor=state.get('floor'), seats_leased=100, start_date=date(2026, 6, 1),
                          monthly_rate=Decimal('150000'), status='active'),
        )

    for fn in (_company, _building, _floor, _facility, _inventory, _vendor, _vendor_bill, _lease):
        safe(fn)


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('workspace', '0001_initial'),
        ('facilities', '0003_facility_owner_company'),
        ('inventory', '0001_initial'),
        ('vendors', '0001_initial'),
        ('leases', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
