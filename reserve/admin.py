from django.contrib import admin

from reserve.models import Room, Intem, Other, Plate, Reserve


class CustomRoomAdmin(admin.ModelAdmin):
    model = Room

    list_display = (
        "name",
        "description",
    )
    search_fields = ("name",)
    ordering = ("name",)


class CustomReserveAdmin(admin.ModelAdmin):
    model = Reserve

    list_display = (
        "room",
        "start_date",
        "end_date",
        "is_within",
    )


admin.site.register(Room, CustomRoomAdmin)
admin.site.register(Reserve, CustomReserveAdmin)
admin.site.register(Intem)
admin.site.register(Plate)
admin.site.register(Other)
