import base64

import pytz
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from courses.models import (Coupon, Course, Direction, Partner, PartnerVideo,
                            UserCoupon, UserVideo, Video)
from users_alfacrm.models import AlfaCRMUser, City, Coordinaties


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class VideoSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    points = serializers.IntegerField(read_only=True)
    preview = Base64ImageField(required=False, allow_null=True)
    viewed = serializers.SerializerMethodField()

    def get_viewed(self, videos):
        user = self.context["request"].user
        if user.is_authenticated:
            try:
                user_video = UserVideo.objects.get(user=user, video=videos)
                return user_video.viewed
            except UserVideo.DoesNotExist:
                pass
        return False

    class Meta:
        model = Video
        fields = "__all__"


class PartnerVideoSerializer(serializers.ModelSerializer):
    partner_preview = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = PartnerVideo
        fields = ["id", "promo_url", "points", "partner_preview"]


class CouponSerializer(serializers.ModelSerializer):
    can_redeem = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    video_coupone = VideoSerializer(read_only=True)
    video_coupone_partner = PartnerVideoSerializer(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            "id",
            "image",
            "description",
            "points_required",
            "quantity",
            "can_redeem",
            "video_coupone",
            "video_coupone_partner"
        ]

    def get_can_redeem(self, obj):
        user = self.context["request"].user
        return (
            user.balance >= obj.points_required and
            obj.quantity > 0 and
            not UserCoupon.objects.filter(user=user, coupon=obj).exists()
        )


class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    coupon_title = serializers.CharField(source="coupon.title")
    user_name = serializers.CharField(source="user.name")
    user_email = serializers.CharField(source="user.email")
    user_balance = serializers.CharField(source="user.balance")
    partner_name = serializers.CharField(source="coupon.partner")
    redeemed_at_display = serializers.SerializerMethodField()

    class Meta:
        model = UserCoupon
        fields = [
            "id",
            "user_email",
            "user_name",
            "user_balance",
            "coupon",
            "coupon_title",
            "partner_name",
            "redeemed_at_display",
        ]

    def get_redeemed_at_display(self, obj):
        if obj.redeemed_at:
            local_tz = pytz.timezone("Europe/Moscow")
            return obj.redeemed_at.astimezone(local_tz).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        return ""


class CouponRedemptionSerializer(serializers.Serializer):
    coupon_id = serializers.IntegerField()


class PartnerSerializer(serializers.ModelSerializer):
    coupons = CouponSerializer(many=True, read_only=True)

    class Meta:
        model = Partner
        fields = [
            "id",
            "coupons",
        ]

    def get_videos(self, obj):
        user = self.context["request"].user
        partner_videos = obj.videos.all()
        serialized_videos = PartnerVideoSerializer(
            partner_videos, many=True
        ).data

        if user.is_authenticated:
            viewed_videos = UserVideo.objects.filter(
                user=user, partner_video__in=partner_videos, viewed=True
            )
            viewed_video_ids = set(
                viewed_videos.values_list("partner_video__id", flat=True)
            )
            for video in serialized_videos:
                video_obj = PartnerVideo.objects.get(id=video["id"])
                video["viewed"] = video_obj.id in viewed_video_ids
        return serialized_videos


class UserVideoSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    partner_video = PartnerVideoSerializer(read_only=True)

    class Meta:
        model = UserVideo
        fields = "__all__"


class CoordinatiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinaties
        fields = ('lat', 'lon')


class CitySerializer(serializers.ModelSerializer):
    coordinaties = CoordinatiesSerializer(read_only=True)

    class Meta:
        model = City
        fields = (
            "id",
            "coordinaties",
            "district",
            "name",
            "population",
            "subject",
        )


class AlfaCRMUserSerializer(UserSerializer):
    auth_token = serializers.SerializerMethodField()
    city = CitySerializer(required=False)

    class Meta:
        model = AlfaCRMUser
        fields = (
            "email",
            "phone",
            "id",
            "name",
            "auth_token",
            "password",
            "city"
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_auth_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def create(self, validated_data):
        city_data = validated_data.pop("city", None)
        if city_data is not None:
            try:
                city = City.objects.get(pk=city_data["id"])
            except City.DoesNotExist:
                raise serializers.ValidationError("Invalid city.")
            validated_data["city"] = city
        return AlfaCRMUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        city_data = validated_data.pop("city", None)
        if city_data is not None:
            city_id = city_data.get("id")
            if city_id is not None:
                try:
                    city = City.objects.get(pk=city_id)
                except City.DoesNotExist:
                    raise serializers.ValidationError("Invalid city.")
                instance.city = city
        return super().update(instance, validated_data)


class AlfaCRMUserListSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    city_name = serializers.SerializerMethodField()
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = AlfaCRMUser
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "avatar",
            "city",
            "city_name"
        )

    def get_city_name(self, obj):
        city = obj.city
        if city is not None:
            return city.name
        return None

    def update(self, instance, validated_data):
        city = validated_data.get("city")
        if city is not None:
            if not isinstance(city, City):
                raise serializers.ValidationError("Invalid city.")
            instance.city = city
        return super().update(instance, validated_data)
