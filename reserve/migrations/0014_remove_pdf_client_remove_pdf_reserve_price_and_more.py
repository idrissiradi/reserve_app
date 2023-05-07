# Generated by Django 4.2 on 2023-04-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reserve", "0013_alter_pdf_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pdf",
            name="client",
        ),
        migrations.RemoveField(
            model_name="pdf",
            name="reserve_price",
        ),
        migrations.AddField(
            model_name="reserve",
            name="client",
            field=models.CharField(default="test", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reserve",
            name="price",
            field=models.DecimalField(decimal_places=2, default=12.02, max_digits=15),
            preserve_default=False,
        ),
    ]
