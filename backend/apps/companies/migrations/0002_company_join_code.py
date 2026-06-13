import secrets
import string

from django.db import migrations, models

_ALPHABET = ''.join(
    c for c in (string.ascii_uppercase + string.digits) if c not in 'O0I1'
)


def _gen(length=8):
    return ''.join(secrets.choice(_ALPHABET) for _ in range(length))


def backfill_join_codes(apps, schema_editor):
    """Give every existing company a unique join code."""
    Company = apps.get_model('companies', 'Company')
    used = set(
        Company.objects.exclude(join_code='').values_list('join_code', flat=True)
    )
    for company in Company.objects.filter(join_code=''):
        code = _gen()
        while code in used:
            code = _gen()
        used.add(code)
        company.join_code = code
        company.save(update_fields=['join_code'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        # 1) Add as a plain (non-unique) column so existing rows can coexist.
        migrations.AddField(
            model_name='company',
            name='join_code',
            field=models.CharField(blank=True, default='', max_length=12),
            preserve_default=False,
        ),
        # 2) Backfill unique codes for any pre-existing companies.
        migrations.RunPython(backfill_join_codes, noop),
        # 3) Enforce uniqueness now that every row has a distinct value.
        migrations.AlterField(
            model_name='company',
            name='join_code',
            field=models.CharField(
                blank=True,
                help_text='Share with employees so they can self-register into this company.',
                max_length=12,
                unique=True,
            ),
        ),
    ]
