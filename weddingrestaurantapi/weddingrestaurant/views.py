from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from weddingrestaurant import paginators
from weddingrestaurant.models import User, UserRole, Staff, WeddingHall, WeddingHallImage, WeddingHallPrice, EventType, \
    Service, Drink, FoodType, Food, WeddingBooking, Feedback
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


class FeedbackViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
