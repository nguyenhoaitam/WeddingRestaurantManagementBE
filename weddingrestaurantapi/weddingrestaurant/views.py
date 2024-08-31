from django.contrib.auth.hashers import make_password
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

    def create(self, request, *args, **kwargs):
        user_data = request.data.copy()

        user_role = UserRole.objects.get(name='customer')
        user_data['user_role'] = user_role.id

        user_serializer = self.get_serializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        Customer.objects.create(user=user)

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
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)
        return queryset


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
