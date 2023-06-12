from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from django.utils.safestring import mark_safe
from rest_framework.response import Response

from .models import (Coupon, Course, Direction, Partner, PartnerVideo,
                     UserCoupon, Video)


class VideoInline(admin.TabularInline):
    model = Video


class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title",)
    inlines = [VideoInline]
    extra = 30


class CouponAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["points_required"].required = True
        self.fields["quantity"].required = True
        self.fields["image"].required = True

    class Meta:
        model = Coupon
        fields = "__all__"


class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "coupon_type",
        "partner",
        "points_required",
    )
    list_filter = ("coupon_type",)
    form = CouponAdminForm

    def get_fieldsets(self, request, obj=None):
        if obj and obj.coupon_type == "partner":
            return (
                (
                    None,
                    {
                        "fields": (
                            "title",
                            "coupon_type",
                            "description",
                            "partner",
                            "partner_name",
                            "points_required",
                            "quantity",
                            "video_coupone_partner",
                            "image",
                        ),
                    },
                ),
            )
        if obj and obj.coupon_type == "own":
            return (
                (
                    None,
                    {
                        "fields": (
                            "title",
                            "coupon_type",
                            "description",
                            "points_required",
                            "quantity",
                            "video_coupone",
                            "image",
                        ),
                    },
                ),
            )
        return super().get_fieldsets(request, obj)


class UserCouponAdmin(admin.ModelAdmin):
    exclude = ("redeemed_at",)
    list_display = ("id", "user", "coupon", "redeemed_at")
    raw_id_fields = ("user",)
    list_filter = (
        "redeemed_at",
        "coupon",
    )

    actions = ["redeem_coupon_admin"]

    def redeem_coupon(self, request, pk=None):
        user_coupon = UserCoupon.objects.get(pk=pk)
        coupon = user_coupon.coupon

        user = user_coupon.user
        if user.balance < coupon.points_required:
            return Response(
                {
                    "error": "У пользователя недостаточно баллов "
                    "для получения купона"
                }
            )
        if user_coupon.redeemed_at is not None:
            return Response({"error": "Этот купон уже использован"})
        if coupon.quantity == 0:
            return Response({"error": "Купоны закончились"})

        with transaction.atomic():
            user.balance -= coupon.points_required
            user.save()
            user_coupon.redeemed_at = timezone.now()
            user_coupon.save()
            coupon.quantity -= 1
            coupon.save()

        return Response({"success": True})

    def redeem_coupon_admin(self, request, queryset):
        for coupon in queryset:
            if not UserCoupon.objects.filter(pk=coupon.pk).exists():
                messages.warning(
                    request,
                    mark_safe(f"Купон с ID {coupon.pk} не существует"),
                )
                continue
            response = self.redeem_coupon(request, pk=coupon.pk)
            if response.status_code == 200 and "success" in response.data:
                messages.success(
                    request,
                    mark_safe(
                        f"Купон с ID {coupon.pk} был использован "
                        f"{request.user}"
                    ),
                )
            else:
                messages.warning(
                    request,
                    mark_safe(
                        f"Ошибка при использовании купона ID {coupon.pk}: "
                        f"{response.data.get('error')}"
                    ),
                )

    redeem_coupon_admin.short_description = "Списать баллы за купон"


class PartnerVideoInline(admin.TabularInline):
    model = PartnerVideo


class PartnerAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [PartnerVideoInline]
    # extra = 30


class VideoAdmin(admin.ModelAdmin):
    search_fields = ("description",)
    list_display = ("description", "course")
    list_filter = ("course",)


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(UserCoupon, UserCouponAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Direction)
