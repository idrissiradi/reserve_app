import datetime
from io import BytesIO
from json import dumps

from celery import shared_task
from num2words import num2words
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.views.generic import View, FormView, ListView, DetailView, TemplateView
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from users.mixins import AdminOnlyView, LoggedInOnlyView
from users.models import User
from reserve.forms import BonForm, RoomCreateForm, ReserveCreateForm, PdfOtherCreateForm
from reserve.models import Bon, Pdf, Room, Intem, Other, Plate, Reserve


class RoomListView(LoggedInOnlyView, ListView):
    """Home page"""

    model = Room
    ordering = "-created_at"
    context_object_name = "rooms"
    template_name = "reserve/home.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ReserveListView(LoggedInOnlyView, ListView):
    """Reservation List page"""

    model = Reserve
    ordering = "-created_at"
    context_object_name = "reserves"
    template_name = "reserve/all_reserve.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required(login_url=reverse_lazy("users:login"))
def delete_room(request, pk):
    user = request.user
    if user.admin:
        Room.objects.filter(pk=pk).delete()
    return redirect(reverse("reserve:home"))


class RoomDetailView(LoggedInOnlyView, DetailView):
    """Room details"""

    model = Room
    template_name = "reserve/room_detail.html"

    def get_context_data(self, **kwargs):
        context = super(RoomDetailView, self).get_context_data(**kwargs)
        context["reservations"] = Reserve.objects.filter(room=self.object).all().order_by("-created_at")  # type: ignore
        context["data"] = dumps(list(Reserve.objects.filter(room=self.object).values()), default=str)  # type: ignore
        return context


class StatisticsView(LoggedInOnlyView, TemplateView):
    template_name = "reserve/statistics.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        date = request.GET.get("reserve_date", None)  # type: ignore
        month = request.GET.get("month", None)
        payment_type = request.GET.get("payment_type", None)

        reservations = Reserve.objects.all()

        if date == "":
            date = None
        if date is not None:
            y, m, d = date.split("-")
            date = datetime.date(int(y), int(m), int(d))
            reservations = Reserve.objects.filter(created_at=date).all()

        if month == "":
            month = None
        if month is not None:
            reservations = Reserve.objects.filter(created_at__month=month).all()

        if payment_type == "":
            payment_type = None
        if payment_type is not None:
            reservations = Reserve.objects.filter(pdf__payment_type=payment_type).all()

        total = 0.0
        total_payed = 0.0
        total_no_payed = 0.0
        other_total = 0.00

        for reserve in reservations:
            others = Other.objects.filter(others=reserve).all()
            for other in others:
                other_total = other_total + float(other.price)
            total = float(total) + float(reserve.price) + other_total
            pdfs = Pdf.objects.filter(reserve=reserve, type="f", payment_type="e").all()

            for pdf in pdfs:
                if pdf.is_payed:
                    total_payed = float(total_payed) + float(reserve.price)
                else:
                    total_no_payed = float(total_no_payed) + float(reserve.price)
        bons = Bon.objects.all()
        for bon in bons:
            total = total - float(bon.price)
        interm = Intem.objects.all()
        data = []

        for i in interm:
            interm_total = 0.00
            type = i.type
            reserves = Reserve.objects.filter(interm__type=i.type).all()
            for re in reserves:
                interm_total = float(interm_total) + float(re.price)
            data.append({"type": type, "total": interm_total})

        context["total"] = total
        context["total_payed"] = total_payed
        context["total_no_payed"] = total_no_payed
        context["reservations"] = reservations
        context["interm"] = data

        return self.render_to_response(context)


class CreateRoom(LoggedInOnlyView, AdminOnlyView, FormView):
    """New room"""

    template_name = "reserve/create_newroom.html"
    form_class = RoomCreateForm
    success_url = reverse_lazy("reserve:home")

    def form_valid(self, form):
        form.save()  # type: ignore
        return super().form_valid(form)


class CreateBon(LoggedInOnlyView, AdminOnlyView, FormView):
    """New bon"""

    template_name = "reserve/create_newbon.html"
    form_class = BonForm
    success_url = reverse_lazy("reserve:create_bon")

    def form_valid(self, form):
        form.save()  # type: ignore
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateBon, self).get_context_data(**kwargs)
        context["bons"] = Bon.objects.all().order_by("-created_at")  # type: ignore
        return context


@login_required(login_url=reverse_lazy("users:login"))
@require_http_methods(["GET", "POST"])
def create_reserve(request, pk: int):
    """New reservation"""

    if request.method == "POST":
        form = ReserveCreateForm(request.POST)
        if form.is_valid():
            user = request.user
            room = Room.objects.get(pk=pk)
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            client = form.cleaned_data["client"]
            price = form.cleaned_data["price"]

            reserves_list = Reserve.objects.filter(room__id=pk)

            for rv in reserves_list:
                if (
                    rv.start_date <= start_date <= rv.end_date
                    or rv.start_date <= end_date <= rv.end_date
                ):
                    return render(
                        request,
                        "reserve/create_newreserve.html",
                        {"pk": pk, "error": "Données invalides", "form": form},
                    )

            Reserve.objects.create(
                user=user,
                room=room,
                start_date=start_date,
                end_date=end_date,
                client=client,
                price=price,
            )
            return redirect(reverse("reserve:room_detail", kwargs={"pk": pk}))
    else:
        form = ReserveCreateForm()
    return render(request, "reserve/create_newreserve.html", {"pk": pk, "form": form})


@login_required(login_url=reverse_lazy("users:login"))
def delete_reserve(request, pk: int, reserve_pk: int):
    """Delete reservation"""

    user = request.user
    reserve = Reserve.objects.get(pk=reserve_pk)
    if user.admin or user.id == reserve.user.id:  # type: ignore
        reserve.delete()
    return redirect(reverse("reserve:room_detail", kwargs={"pk": pk}))


@login_required(login_url=reverse_lazy("users:login"))
def update_reserve(request, pk: int, reserve_pk: int):
    """Update reservation"""
    user = request.user
    reserve = Reserve.objects.get(pk=reserve_pk)
    if user.admin or user.id == reserve.user.id:  # type: ignore
        if request.method == "POST":
            form = ReserveCreateForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data["start_date"]
                end_date = form.cleaned_data["end_date"]
                client = form.cleaned_data["client"]
                price = form.cleaned_data["price"]

                reserves_list = Reserve.objects.filter(room__id=pk).exclude(
                    pk=reserve_pk
                )

                for rv in reserves_list:
                    if (
                        rv.start_date <= start_date <= rv.end_date
                        or rv.start_date <= end_date <= rv.end_date
                    ):
                        return redirect(
                            reverse(
                                "reserve:reserve_detail",
                                kwargs={"pk": pk, "reserve_pk": reserve_pk},
                            )
                        )

                Reserve.objects.filter(pk=reserve_pk).update(
                    start_date=start_date, end_date=end_date, client=client, price=price
                )
                return redirect(
                    reverse(
                        "reserve:reserve_detail",
                        kwargs={"pk": pk, "reserve_pk": reserve_pk},
                    )
                )
    return redirect(
        reverse("reserve:reserve_detail", kwargs={"pk": pk, "reserve_pk": reserve_pk})
    )


class ReserveDetailView(LoggedInOnlyView, DetailView):
    """Reservation details"""

    model = Reserve
    template_name = "reserve/reserve_detail.html"
    pk_url_kwarg = "reserve_pk"
    http_method_names = ["get", "post"]

    def get_context_data(self, **kwargs):
        context = super(ReserveDetailView, self).get_context_data(**kwargs)  # type: ignore
        return context


@login_required(login_url=reverse_lazy("users:login"))
@require_http_methods(["GET", "POST"])
def create_pdf(request, pk: int, reserve_pk: int):
    """Generate a pdf"""
    user = request.user
    reserve = Reserve.objects.get(pk=reserve_pk)
    if user.admin or user.id == reserve.user.id:  # type: ignore
        if request.method == "POST":
            address = request.POST["address"]
            type = request.POST["type"]
            others = request.POST.getlist("other")
            avance = request.POST["avance"]
            payment_type = request.POST["payment_type"]
            cheque_info = request.POST["cheque_info"]
            interm = request.POST["interm"]

            intermid = Intem.objects.get(type=interm)
            reserve = Reserve.objects.get(pk=reserve_pk)
            days = request.POST["days"]

            pdf = Pdf.objects.create(
                reserve=reserve,
                address=address,
                days=days,
                avance=avance,
            )

            Reserve.objects.filter(pk=reserve_pk).update(interm=intermid)

            if "is_payed" in request.POST:
                pdf.is_payed = True
            if type == "Facture":
                pdf.type = "f"
            elif type == "Devis":
                pdf.type = "d"
            else:
                pdf.type = "b"

            if payment_type == "Cheque":
                pdf.payment_type = "c"
                pdf.cheque_info = cheque_info
            elif payment_type == "Espece":
                pdf.payment_type = "e"
            else:
                pdf.payment_type = "t"

            for other in others:
                pdf_other = Other.objects.get(pk=other)  # type: ignore
                reserve.other.add(pdf_other)  # type: ignore

            pdf.save()

        else:
            interms = Intem.objects.all()
            days = reserve.end_date - reserve.start_date
            others = Other.objects.all().order_by("name")
            pdfs = (
                Pdf.objects.filter(reserve__id=reserve_pk).all().order_by("-created_at")
            )
            return render(
                request,
                "reserve/pdf.html",
                {
                    "pk": pk,
                    "reserve_pk": reserve_pk,
                    "days": days.days,
                    "others": others,
                    "pdfs": pdfs,
                    "client": reserve.client,
                    "price": reserve.price,
                    "interms": interms,
                },
            )

    return redirect(
        reverse(
            "reserve:reserve_detail",
            kwargs={"pk": pk, "reserve_pk": reserve_pk},
        )
    )


@login_required(login_url=reverse_lazy("users:login"))
@require_http_methods(["GET", "POST"])
def create_pdf_other(request, pk: int, reserve_pk: int):
    """add others"""
    user = request.user
    reserve = Reserve.objects.get(pk=reserve_pk)
    if user.admin or user.id == reserve.user.id:  # type: ignore
        if request.method == "POST":
            form = PdfOtherCreateForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data["name"]
                price = form.cleaned_data["price"]
                Other.objects.create(name=name, price=price)
                return redirect(
                    reverse(
                        "reserve:pdf",
                        kwargs={"pk": pk, "reserve_pk": reserve_pk},
                    )
                )
        else:
            form = ReserveCreateForm()
            return render(
                request,
                "reserve/pdf_other.html",
                {"pk": pk, "reserve_pk": reserve_pk, "form": form},
            )

    return redirect(
        reverse(
            "reserve:pdf",
            kwargs={"pk": pk, "reserve_pk": reserve_pk},
        )
    )


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)  # type: ignore
    pdf = pisa.CreatePDF(
        BytesIO(html.encode("UTF-8")),
        result,
        encoding="UTF-8",
    )
    if not pdf.err:  # type: ignore
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    value = result.getvalue()
    result.close()
    return value


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        pdf = Pdf.objects.get(pk=kwargs["pdf_pk"])
        reservation = Reserve.objects.get(pk=kwargs["reserve_pk"])  # type: ignore
        user = request.user
        room = Room.objects.get(pk=kwargs["pk"])
        price = reservation.price
        client = reservation.client
        others = Other.objects.filter(others=reservation).all()
        other_total = 0.0
        avance = 0.0
        res_total = 0.0

        plates = Plate.objects.filter(reserve=reservation).all()
        for pl in plates:
            price = pl.price * pl.number
            res_total = res_total + float(price)

        for other in others:
            other_total: float = other_total + float(other.price)

        if pdf.avance is not None:
            avance = pdf.avance

        total: float = float(price) + res_total + other_total - float(avance)

        total_word = num2words(total, lang="fr")
        context = {
            "pdf": pdf,
            "user": user,
            "room": room,
            "price": price,
            "others": others,
            "total": total,
            "total_word": total_word,
            "client": client,
            "plates": plates,
        }

        pdf = render_to_pdf("pdf/invoice.html", context)

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=invoice.pdf"
        return response


class GenerateBonPdf(View):
    def get(self, request, *args, **kwargs):
        bon = Bon.objects.get(pk=kwargs["pk"])
        total_word = num2words(bon.price, lang="fr")

        context = {"bon": bon, "total_word": total_word}

        pdf = render_to_pdf("pdf/bon.html", context)

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=bon.pdf"
        return response


@shared_task
def send_rapport():
    date = datetime.datetime.now()
    reservations = Reserve.objects.filter(created_at=date.date).all()

    total = 0.0
    res_total = 0.0
    other_total = 0.00
    charge_total = 0.00
    total_day = 0.00
    payment_type = []
    interm = []

    total_espece = 0.00

    for reserve in reservations:
        for other in reserve.other:
            other_total = other_total + other.price
        total = float(total) + float(reserve.price) + other_total

        plates = Plate.objects.filter(reserve=reserve).all()
        for pl in plates:
            price = pl.price * pl.number
            res_total = res_total + float(price)

        interms = Intem.objects.filter(reserve=reserve).all()
        for intm in interms:
            interm.append(intm.type)

        pdfs_check = Pdf.objects.filter(created_at=date.date, payment_type="c").all()
        pdfs_tpe = Pdf.objects.filter(created_at=date.date, payment_type="t").all()
        pdfs = Pdf.objects.filter(created_at=date.date, payment_type="e").all()

        pdfs_facture = Pdf.objects.filter(created_at=date.date, type="f").all()

        for pdf in pdfs:
            total_espece = total_espece + float(pdf.reserve.price)

        for pdf in pdfs_facture:
            payment_type.append(pdf.payment_type)

    bons = Bon.objects.all()
    for bon in bons:
        total = total - float(bon.price)

    total_day = total - charge_total
    subject, from_email, to = (
        "Le rapport",
        "from",
        "to",
    )
    text_content = "This is an important message."
    html_content = f"""
        <html>
            <body>
            <h1>Chiffre d'affaire de jours</h1>
                <div>
                    <h3>Le Chifre d'affaire du {date.day}/{date.month}/{date.year}</h3>
                    <p>CA logement {total} TTC</p>
                    <p>CA restaurant {res_total} TTC</p>
                    <p>Le CA total du jour {total_day} TTC</p>
                    <p>Type de payment {payment_type} </p>
                    <p>Total des achats {charge_total} MAD</p>
                    <p>Solde Espéce {total_espece} MAD</p>
                    <p>Intermediare {interm} </p>
                </div>
            </body>
        </html>
    """
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
