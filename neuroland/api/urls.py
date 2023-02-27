from django.urls import include, path

from rest_framework.routers import DefaultRouter


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]
