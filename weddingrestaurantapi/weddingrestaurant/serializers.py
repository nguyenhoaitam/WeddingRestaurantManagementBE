from rest_framework import serializers
from rest_framework.utils import representation

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

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['user_role'] = instance.user_role.name if instance.user_role else None
    #     return rep


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    user_role = serializers.CharField(source='user_role.name', read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        avatar = getattr(instance, 'avatar', None)
        if avatar:
            rep['avatar'] = instance.avatar.url

        if hasattr(instance, 'customer'):
            rep['customer'] = CustomerSerializer(instance.customer).data
        if hasattr(instance, 'staff'):
            rep['staff'] = StaffSerializer(instance.staff).data

        return rep

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'avatar', 'phone', 'user_role',
                  'customer', 'staff']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class WeddingHallImageSerializer(serializers.ModelSerializer):

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['path'] = instance.path.url
    #
    #     return rep
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        path = getattr(instance, 'path', None)
        if path:
            rep['path'] = instance.path.url

        return rep

    class Meta:
        model = WeddingHallImage
        fields = '__all__'


class WeddingHallPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingHallPrice
        fields = '__all__'


class WeddingHallSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    prices = WeddingHallPriceSerializer(many=True, source='weddinghallprice_set')

    def get_images(self, obj):
        return [image.path.url for image in obj.get_images()]

    class Meta:
        model = WeddingHall
        fields = ['id', 'name', 'description', 'capacity', 'is_active', 'images', 'prices']


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        image = getattr(instance, 'image', None)
        if image:
            rep['image'] = instance.image.url

        return rep

    class Meta:
        model = Service
        fields = '__all__'


class DrinkSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        image = getattr(instance, 'image', None)
        if image:
            rep['image'] = instance.image.url

        return rep

    class Meta:
        model = Drink
        fields = '__all__'


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        image = getattr(instance, 'image', None)
        if image:
            rep['image'] = instance.image.url

        return rep

    class Meta:
        model = Food
        fields = '__all__'


class WeddingBookingSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True)
    drinks = DrinkSerializer(many=True)
    services = ServiceSerializer(many=True)

    # def get_user(self, feedback):
    #     return UserSerializer(feedback.user, context={"request": self.context.get('request')}).data

    class Meta:
        model = WeddingBooking
        fields = ['id', 'name', 'description', 'table_quantity', 'rental_date', 'payment_method', 'payment_status',
                  'total_price', 'created_date', 'event_type', 'customer', 'foods', 'drinks', 'services']


class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, feedback):
        return UserSerializer(feedback.user, context={"request": self.context.get('request')}).data

    class Meta:
        model = Feedback
        fields = ['id', 'content', 'rating', 'created_date', 'updated_date', 'user']
