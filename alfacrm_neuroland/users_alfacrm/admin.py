import os

from django import forms
from django.contrib import admin

from .firebase import send_firebase_notification
from .models import AlfaCRMUser, Notification, UserToken

# from .onesignal import send_onesignal_notification

app_id = os.getenv("APP_ID", default="app_id")
api_key = os.getenv("REST_API_KEY", default="api_key")


class AlfaCRMUserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "avatar",
        "balance",
        "referral_code",
        "referrer",
        "city",
    )
    fields = (
        "name",
        "email",
        "phone",
        "avatar",
        "balance",
        "referral_code",
        "referrer",
        "city",
    )


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('title', 'message')


class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    list_display = ('title', 'message')

    def save_model(self, request, obj, form, change):
        # users = AlfaCRMUser.objects.all()
        fcm_tokens = UserToken.objects.values_list('fcm_token', flat=True)
        for fcm_token in fcm_tokens:
            send_firebase_notification(obj.title, obj.message, fcm_token)
        # send_onesignal_notification(obj.title, obj.message, users)
        super().save_model(request, obj, form, change)


# admin.site.register(Notification, NotificationAdmin)
admin.site.register(AlfaCRMUser, AlfaCRMUserAdmin)
