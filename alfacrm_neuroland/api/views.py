from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (AlfaCRMUserListSerializer, CouponSerializer,
                             CourseSerializer, DirectionSerializer,
                             PartnerSerializer, UserCouponSerializer,
                             UserVideoSerializer, VideoSerializer)
from courses.models import (Coupon, Course, Direction, Partner, PartnerVideo,
                            UserCoupon, UserVideo, Video)


class VideoListView(APIView):
    def get(self, request):
        videos = Video.objects.all()
        user = request.user
        balance = user.balance if user.is_authenticated else 0
        own_coupons = Coupon.objects.filter(coupon_type="own")
        serializer = VideoSerializer(
            videos, many=True, context={"request": request}
        )
        coupon_serializer = CouponSerializer(
            own_coupons, many=True, context={"request": request}
        )
        response_data = {
            "directions": DirectionSerializer(
                Direction.objects.all(), many=True
            ).data,
            "balance": balance,
            "videos": serializer.data,
            "coupons": coupon_serializer.data,
        }
        return Response(response_data)


class PartnerListView(APIView):
    def get(self, request):
        user = request.user
        balance = user.balance if user.is_authenticated else 0
        coupons = Coupon.objects.filter(coupon_type="partner")
        serializer = CouponSerializer(
            coupons, many=True, context={"request": request}
        )
        response_data = {"balance": balance, "coupons": serializer.data}
        return Response(response_data)


class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.all().order_by("-created_at")
    serializer_class = DirectionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "mark_as_viewed"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        serializer = VideoSerializer(
            videos, many=True, context={"request": request}
        )
        user = self.request.user
        if user.is_authenticated:
            try:
                user_video = UserVideo.objects.get(user=user, video=videos)
                return user_video.viewed
            except UserVideo.DoesNotExist:
                pass
        return Response({"videos": serializer.data})

    @action(detail=True, methods=["post"], url_path="viewed")
    def mark_as_viewed(self, request, pk=None):
        video = self.get_object()
        user = request.user
        user_video, created = UserVideo.objects.get_or_create(
            user=user,
            video=video,
        )
        if not created and user_video.viewed:
            return Response(
                {"status": "Already marked as viewed"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user_video.viewed = True
        user_video.save()
        user.balance += video.points
        user.save()
        serializer_context = {"request": request} if request else {}
        serializer = self.get_serializer(video, context=serializer_context)
        return Response(
            {
                "status": "Marked as viewed and points added",
                "video": serializer.data,
            }
        )


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "redeem_coupon",
        ]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=True, methods=["post"], url_path="redeem")
    def redeem_coupon(self, request, pk=None):
        coupon = self.get_object()
        user = request.user
        try:
            with transaction.atomic():
                if user.balance < coupon.points_required:
                    return Response(
                        {"error": "Not enough points to get the coupon"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                user_coupons = UserCoupon.objects.filter(
                    user=user, coupon=coupon
                )
                if user_coupons.exists():
                    return Response(
                        {"error": "You have already used this coupon"},
                        status=400,
                    )
                if coupon.quantity == 0:
                    return Response(
                        {"error": "No more coupons available"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                user.balance -= coupon.points_required
                user.save()
                user_coupon = UserCoupon(user=user, coupon=coupon)
                user_coupon.save()
                coupon.quantity -= 1
                coupon.save()
                user_coupon.redeemed_at = timezone.now()
                user_coupon.save()
        except Exception as e:
            return Response({"error": str(e)})
        return Response({"success": True})


class UserVideoViewSet(viewsets.ModelViewSet):
    queryset = UserVideo.objects.all()
    serializer_class = UserVideoSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "get_partner_coupons",
            "mark_as_viewed",
        ]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=True, methods=["get"], url_path="partner-coupons")
    def get_partner_coupons(self, request, pk=None):
        partner = self.get_object()
        coupons = Coupon.objects.filter(partner=partner)
        serializer = CouponSerializer(
            coupons, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="viewed")
    def mark_as_viewed(self, request, pk=None):
        partner_video = PartnerVideo.objects.get(pk=pk)
        user = request.user
        user_video, created = UserVideo.objects.get_or_create(
            user=user, partner_video=partner_video
        )
        if not created and user_video.viewed:
            return Response(
                {"status": "Already marked as viewed"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user_video.viewed = True
        user_video.save()
        user.balance += partner_video.points
        user.save()
        return Response({"status": "Marked as viewed and points added"})


class UserCouponViewSet(viewsets.ModelViewSet):
    queryset = UserCoupon.objects.all()
    serializer_class = UserCouponSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "get_used_user_coupons"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=["get"], url_path="used-coupons")
    def get_used_user_coupons(self, request):
        user = request.user
        used_coupons = UserCoupon.objects.filter(user=user, redeemed_at=True)
        serializer = UserCouponSerializer(used_coupons, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        try:
            user_id = int(self.request.user.id)
            return UserCoupon.objects.filter(user=user_id)
        except (AttributeError, TypeError):
            return UserCoupon.objects.none()


class UserCouponsAPIView(APIView):
    def get(self, request):
        user = request.user
        user_coupons = UserCoupon.objects.filter(
            user=user,
            redeemed_at__isnull=False
        )
        coupons = set([user.coupon for user in user_coupons])
        serializer = AlfaCRMUserListSerializer(
            user, context={"request": request}
        )
        coupon_serializer = CouponSerializer(
            coupons, many=True, context={"request": request}
        )
        response_data = {
            "user": serializer.data,
            "coupons": coupon_serializer.data,
        }
        return Response(response_data)
