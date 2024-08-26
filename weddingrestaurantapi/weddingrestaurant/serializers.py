from rest_framework import serializers
from weddingrestaurant.models import User, UserRole, Staff, Customer, WeddingHall, WeddingHallImage, WeddingHallPrice, \
    EventType, Service, FoodType, Food, Drink, WeddingBooking, Feedback


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url

        return rep


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        avatar = getattr(instance, 'avatar', None)
        if avatar:
            rep['avatar'] = instance.avatar.url

        return rep

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'avatar', 'phone', 'user_role']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class WeddingHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingHall
        fields = '__all__'


class WeddingHallImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingHallImage
        fields = '__all__'


class WeddingHallPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingHallPrice
        fields = '__all__'


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class WeddingBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingBooking
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'