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
    customer = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    user_role = serializers.CharField()

    def get_customer(self, obj):
        if hasattr(obj, 'customer'):
            return CustomerSerializer(obj.customer).data
        return None

    def get_staff(self, obj):
        if hasattr(obj, 'staff'):
            return StaffSerializer(obj.staff).data
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        avatar = getattr(instance, 'avatar', None)
        if avatar:
            rep['avatar'] = instance.avatar.url

        user_role = instance.user_role.name if instance.user_role else None

        if user_role == 'customer':
            rep.pop('staff', None)
        elif user_role == 'staff':
            rep.pop('customer', None)

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
    foods = serializers.PrimaryKeyRelatedField(many=True, queryset=Food.objects.all())
    drinks = serializers.PrimaryKeyRelatedField(many=True, queryset=Drink.objects.all())
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())

    # def get_user(self, feedback):
    #     return UserSerializer(feedback.user, context={"request": self.context.get('request')}).data

    class Meta:
        model = WeddingBooking
        fields = ['id', 'name', 'description', 'table_quantity', 'rental_date', 'payment_method', 'payment_status',
                  'total_price', 'created_date', 'event_type', 'customer', 'foods', 'drinks', 'services']

    def validate_foods(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Phải có ít nhất 5 món ăn.")
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, feedback):
        return UserSerializer(feedback.user, context={"request": self.context.get('request')}).data

    class Meta:
        model = Feedback
        fields = ['id', 'content', 'rating', 'created_date', 'updated_date', 'user']
