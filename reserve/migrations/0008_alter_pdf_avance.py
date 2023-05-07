# Generated by Django 4.2 on 2023-04-05 23:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reserve", "0007_alter_pdf_avance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pdf",
            name="avance",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=15, null=True
            ),
        ),
    ]
