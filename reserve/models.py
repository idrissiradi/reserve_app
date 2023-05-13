from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from users.models import User


class BaseModel(models.Model):
    created_at = models.DateField(
        ("créé à"),
        db_index=True,
        default=timezone.now,
    )
    updated_at = models.DateField(("mis à jour à"), auto_now=True)

    class Meta:
        abstract = True


class Room(BaseModel):
    name = models.CharField(("nom de la chambre"), max_length=255)
    description = models.TextField(("détails de la chambre"), blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"


class Other(BaseModel):
    name = models.CharField(("nom de la chambre"), max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "charge"
        verbose_name_plural = "charges"


class Reserve(BaseModel):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="reservations"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )
    client = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    other = models.ManyToManyField(Other, related_name="others", blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    interm = models.ForeignKey(
        "Intem", on_delete=models.CASCADE, related_name="interms", blank=True, null=True
    )

    def clean(self):
        if self.start_date >= self.end_date or self.start_date < timezone.now().date():
            raise ValidationError("Données invalides")

    def __str__(self) -> str:
        return f"{self.client} {self.room}"

    @property
    def has_started(self) -> bool:
        now = timezone.now()
        return self.start_date <= now.date()

    @property
    def has_finished(self) -> bool:
        now = timezone.now()
        return self.end_date <= now.date()

    @property
    def is_within(self) -> bool:
        now = timezone.now()
        return self.start_date <= now.date() <= self.end_date


class Plate(BaseModel):
    TYPE_BREAKFAST = "B"
    TYPE_LUNCH = "L"
    TYPE_DINNER = "D"

    TYPE_CHOICES = [
        (TYPE_BREAKFAST, "petit déjeuner"),
        (TYPE_LUNCH, "déjeuner"),
        (TYPE_DINNER, "dîner"),
    ]
    price = models.DecimalField(max_digits=15, decimal_places=2)
    number = models.IntegerField()
    reserve = models.ForeignKey(
        Reserve, on_delete=models.CASCADE, related_name="plates"
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.reserve} {self.type}"

    class Meta:
        verbose_name = "plat"
        verbose_name_plural = "plats"


class Intem(BaseModel):
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.type}"

    class Meta:
        verbose_name = "intermédiaire"
        verbose_name_plural = "intermédiaires"


class Pdf(BaseModel):
    TYPE_FACTURE = "F"
    TYPE_DEVIS = "D"
    TYPE_BON = "B"

    TYPE_ESPECE = "E"
    TYPE_CHEQUE = "C"
    TYPE_TPE = "T"

    TYPE_CHOICES = [
        (TYPE_FACTURE, "Facture"),
        (TYPE_DEVIS, "Devis"),
        (TYPE_BON, "Bon"),
    ]

    TYPE_PAYMENT_CHOICES = [
        (TYPE_ESPECE, "Espece"),
        (TYPE_CHEQUE, "Cheque"),
        (TYPE_TPE, "TPE"),
    ]
    reserve = models.ForeignKey(Reserve, on_delete=models.CASCADE, related_name="pdf")
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_FACTURE)
    address = models.CharField("Adress", max_length=255, blank=True, null=True)
    days = models.IntegerField()
    is_payed = models.BooleanField(default=False)
    avance = models.DecimalField(max_digits=15, decimal_places=2)  # type: ignore
    payment_type = models.CharField(
        max_length=1, choices=TYPE_PAYMENT_CHOICES, blank=True, null=True
    )
    cheque_info = models.CharField("Cheque info", max_length=255, blank=True, null=True)


class Bon(BaseModel):
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)
