from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from weddingrestaurant import paginators
from weddingrestaurant.models import User, UserRole, Staff, WeddingHall, WeddingHallImage, WeddingHallPrice, EventType, \
    Service, Drink, FoodType, Food, WeddingBooking, Feedback, Customer
from weddingrestaurant import serializers


class UserRoleViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = UserRole.objects.all()
    serializer_class = serializers.UserRoleSerializer


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):  # first_name: tên last_name: họ
        user_data = request.data.copy()

        user_role = UserRole.objects.get(name='customer')
        user_data['user_role'] = user_role.id

        user_serializer = self.get_serializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        full_name = f"{last_name} {first_name}".strip()

        Customer.objects.create(user=user, full_name=full_name)

        headers = self.get_success_headers(user_serializer.data)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Lấy thông tin User đang chứng thực, cập nhật thông tin User
    @action(methods=['get', 'patch'], url_path='current_user', detail=False)
    def current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            data = request.data.copy()  # Tạo một bản sao của dữ liệu để tránh ảnh hưởng đến dữ liệu gốc
            if 'password' in data:
                data['password'] = make_password(data['password'])  # Băm mật khẩu

            serializer = serializers.UserSerializer(instance=user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Cập nhật thông tin Customer nếu có
                if hasattr(user, 'customer'):
                    customer_full_name = data.get('customer_full_name', None)
                    customer_address = data.get('customer_address', None)
                    customer_gender = data.get('customer_gender', None)
                    customer_dob = data.get('customer_dob', None)

                    customer_data = {
                        'full_name': customer_full_name,
                        'address': customer_address,
                        'gender': customer_gender,
                        'dob': customer_dob
                    }
                    customer_serializer = serializers.CustomerSerializer(
                        instance=user.customer,
                        data={k: v for k, v in customer_data.items() if v is not None},
                        partial=True
                    )
                    if customer_serializer.is_valid():
                        customer_serializer.save()

                # Cập nhật thông tin Staff nếu có
                if hasattr(user, 'staff'):
                    staff_full_name = data.get('staff_full_name', None)
                    staff_position = data.get('staff_position', None)
                    staff_salary = data.get('staff_salary', None)
                    staff_address = data.get('staff_address', None)
                    staff_gender = data.get('staff_gender', None)
                    staff_dob = data.get('staff_dob', None)

                    staff_data = {
                        'full_name': staff_full_name,
                        'position': staff_position,
                        'salary': staff_salary,
                        'address': staff_address,
                        'gender': staff_gender,
                        'dob': staff_dob
                    }
                    staff_serializer = serializers.StaffSerializer(
                        instance=user.staff,
                        data={k: v for k, v in staff_data.items() if v is not None},
                        partial=True
                    )
                    if staff_serializer.is_valid():
                        staff_serializer.save()

                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializers.UserSerializer(user).data)


class StaffViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = serializers.StaffSerializer


class CustomerViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = serializers.CustomerSerializer


class WeddingHallViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = WeddingHall.objects.filter(is_active=True).order_by('name')
    serializer_class = serializers.WeddingHallSerializer
    # pagination_class = paginators.HallPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        time = self.request.query_params.get('time', None)
        event_date = self.request.query_params.get('event_date', None)

        # Xử lý kiểm tra ngày
        if event_date:
            event_date = datetime.fromisoformat(event_date)
        else:
            event_date = timezone.now()

        is_weekend = event_date.weekday() >= 5  # T7 và CN

        # Lọc theo tên
        if q:
            queryset = queryset.filter(name__icontains=q)

        # Lọc theo buổi
        if time:
            queryset = queryset.filter(weddinghallprice__time=time)

        # Lọc theo min_price
        if min_price is not None:
            queryset = queryset.filter(
                weddinghallprice__price__gte=min_price,
                weddinghallprice__is_weekend=is_weekend,
                weddinghallprice__time=time
            ).distinct()

        # Lọc theo max_price
        if max_price is not None:
            queryset = queryset.filter(
                weddinghallprice__price__lte=max_price,
                weddinghallprice__is_weekend=is_weekend,
                weddinghallprice__time=time
            ).distinct()

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Lấy giá cho từng sảnh tiệc
        for hall in serializer.data:
            event_date = request.query_params.get('event_date')
            time = request.query_params.get('time')
            is_weekend_event = False

            if event_date:
                event_date = datetime.fromisoformat(event_date)
                is_weekend_event = event_date.weekday() >= 5  # Xác định nếu là cuối tuần
            else:
                # Nếu không có event_date, sử dụng ngày hiện tại
                event_date = timezone.now()
                is_weekend_event = event_date.weekday() >= 5  # Cập nhật is_weekend_event

            # Lọc giá theo buổi và ngày
            if time:
                hall['prices'] = serializers.WeddingHallPriceSerializer(
                    WeddingHallPrice.objects.filter(
                        wedding_hall=hall['id'],
                        is_weekend=is_weekend_event,
                        time=time
                    ),
                    many=True
                ).data
            else:
                # Nếu không có time, lấy tất cả giá cho ngày hiện tại
                hall['prices'] = serializers.WeddingHallPriceSerializer(
                    WeddingHallPrice.objects.filter(
                        wedding_hall=hall['id'],
                        is_weekend=is_weekend_event
                    ),
                    many=True
                ).data

        return Response(serializer.data)


class WeddingHallImageViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = WeddingHallImage.objects.all()
    serializer_class = serializers.WeddingHallImageSerializer


class WeddingHallPriceViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = WeddingHallPrice.objects.all()
    serializer_class = serializers.WeddingHallPriceSerializer


class EventTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = EventType.objects.all()
    serializer_class = serializers.EventTypeSerializer


class ServiceViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = serializers.ServiceSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)
        return queryset


class DrinkViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Drink.objects.filter(is_active=True)
    serializer_class = serializers.DrinkSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)
        return queryset


class FoodTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = FoodType.objects.all()
    serializer_class = serializers.FoodTypeSerializer

    @action(methods=['get'], detail=True, url_path='foods')
    def get_foods(self, request, pk=None):
        try:
            food_type = FoodType.objects.get(pk=pk)
        except FoodType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        foods = food_type.food_set.filter(is_active=True)

        q = request.query_params.get('q')
        if q:
            foods = foods.filter(name__icontains=q)

        serialized_foods = serializers.FoodSerializer(foods, many=True, context={"request": request})
        return Response(serialized_foods.data, status=status.HTTP_200_OK)


class FoodViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Food.objects.filter(is_active=True)
    serializer_class = serializers.FoodSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            foodtype_id = self.request.query_params.get('foodtype_id')
            if foodtype_id:
                queryset = queryset.filter(food_type_id=foodtype_id)

        return queryset


class WeddingBookingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    queryset = WeddingBooking.objects.all()
    serializer_class = serializers.WeddingBookingSerializer


class FeedbackViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
