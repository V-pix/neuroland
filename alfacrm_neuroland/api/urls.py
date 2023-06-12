from django.urls import include, path
from rest_framework import routers

from users_alfacrm.views import (CityViewSet, CustomAuthToken,
                                 RefreshTokenView, create_lead, delete_account,
                                 get_telegram_link, invite_user)

from .views import (CouponViewSet, CourseViewSet, DirectionViewSet,
                    PartnerListView, PartnerViewSet, UserCouponsAPIView,
                    UserCouponViewSet, UserVideoViewSet, VideoListView,
                    VideoViewSet)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"videos", VideoViewSet)
router.register(r"coupons", CouponViewSet)
router.register(r"partners", PartnerViewSet)
router.register(r"cities", CityViewSet)
router.register(r"user-coupons", UserCouponViewSet)
router.register(r"directions", DirectionViewSet)
router.register(r"user-videos", UserVideoViewSet)


urlpatterns = [
    path(
        "auth/token/login/", CustomAuthToken.as_view(), name="authentication"
    ),
    path(
        "auth/token/refresh/",
        RefreshTokenView.as_view(),
        name="token_refresh",
    ),
    path("auth/", include("djoser.urls.authtoken")),
    path("registration/", create_lead, name="registration"),
    path("invite/", invite_user, name="invite_user"),
    path("telegram/", get_telegram_link, name="telegram-link"),
    path("course-videos/", VideoListView.as_view(), name="course-videos"),
    path(
        "partner-coupons/", PartnerListView.as_view(), name="partner-coupons"
    ),
    path(
        "videos/<int:pk>/viewed/",
        VideoViewSet.as_view({"post": "viewed"}),
        name="viewed",
    ),
    path(
        "coupons/<int:pk>/redeem/",
        CouponViewSet.as_view({"post": "redeem_coupon"}),
        name="coupon-redeem",
    ),
    path("users/me/", UserCouponsAPIView.as_view(), name='user-coupons'),
    path("user/delete/", delete_account, name="account-delete"),
    path("", include("djoser.urls")),
    path("", include(router.urls)),
]
