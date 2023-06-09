# Generated by Django 4.2 on 2023-04-05 23:23

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reserve", "0009_alter_pdf_reserve_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pdf",
            name="reserve_price",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0"), max_digits=15
            ),
        ),
    ]
