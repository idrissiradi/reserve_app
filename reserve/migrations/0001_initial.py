# Generated by Django 4.1.7 on 2023-03-18 13:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Other",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="créé à",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="mis à jour à"),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="nom de la chambre"),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=15)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Pdf",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="créé à",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="mis à jour à"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("F", "Facture"), ("D", "Devis")],
                        default="F",
                        max_length=1,
                    ),
                ),
                ("client", models.CharField(max_length=255, verbose_name="le client")),
                (
                    "address",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Adress"
                    ),
                ),
                ("number", models.IntegerField(default=1)),
                ("days", models.IntegerField()),
                ("reserve_price", models.DecimalField(decimal_places=2, max_digits=15)),
                ("is_payed", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="créé à",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="mis à jour à"),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="nom de la chambre"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="détails de la chambre"
                    ),
                ),
            ],
            options={
                "verbose_name": "Chambre",
                "verbose_name_plural": "Chambres",
            },
        ),
        migrations.CreateModel(
            name="Reserve",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="créé à",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="mis à jour à"),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="reserve.room",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]