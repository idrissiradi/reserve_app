from django.urls import path

from . import views

app_name = "reserve"

urlpatterns = [
    path("", views.RoomListView.as_view(), name="home"),
    path("list/", views.ReserveListView.as_view(), name="list_reserve"),
    path("statistiques/", views.StatisticsView.as_view(), name="statistics"),
    path("create/", views.CreateRoom.as_view(), name="create_room"),
    path("<int:pk>/", views.RoomDetailView.as_view(), name="room_detail"),
    path("<int:pk>/delete/", views.delete_room, name="delete_room"),
    path("<int:pk>/create/", views.create_reserve, name="create_reserve"),
    path(
        "<int:pk>/<int:reserve_pk>/",
        views.ReserveDetailView.as_view(),
        name="reserve_detail",
    ),
    path(
        "<int:pk>/<int:reserve_pk>/update/", views.update_reserve, name="update_reserve"
    ),
    path(
        "<int:pk>/<int:reserve_pk>/delete/", views.delete_reserve, name="delete_reserve"
    ),
    path("<int:pk>/<int:reserve_pk>/pdf/", views.create_pdf, name="pdf"),
    path("<int:pk>/<int:reserve_pk>/other/", views.create_pdf_other, name="other"),
    path(
        "<int:pk>/<int:reserve_pk>/<int:pdf_pk>/",
        views.GeneratePdf.as_view(),
        name="generate_pdf",
    ),
]
