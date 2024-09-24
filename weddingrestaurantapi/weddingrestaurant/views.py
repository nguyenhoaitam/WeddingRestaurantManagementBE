import hashlib
import urllib
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from weddingrestaurant import paginators
from weddingrestaurant.models import User, UserRole, Staff, WeddingHall, WeddingHallImage, WeddingHallPrice, EventType, \
    Service, Drink, FoodType, Food, WeddingBooking, Feedback, Customer, FoodBookingDetail, DrinkBookingDetail, \
    ServiceBookingDetail
from weddingrestaurant import serializers
from django.http import HttpResponse, HttpRequest, JsonResponse

import time
from datetime import datetime
import json
import requests
import hmac
import random
from django.views.decorators.csrf import csrf_exempt


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

        try:
            user_role = UserRole.objects.get(name='customer')
            user_data['user_role'] = user_role.name
        except UserRole.DoesNotExist:
            return Response({"Thông báo": "Không tìm thấy UserRole Customer"}, status=status.HTTP_400_BAD_REQUEST)

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

    def get_permissions(self):
        if self.action in ['get_wedding_bookings']:
            return [permissions.IsAuthenticated(), ]

        return [permissions.AllowAny(), ]

    @action(detail=True, methods=['get'], url_path='wedding_bookings')
    def get_wedding_bookings(self, request, pk=None):
        try:
            customer = Customer.objects.select_related('user').get(pk=pk)
            bookings = WeddingBooking.objects.filter(customer=customer).prefetch_related('foods', 'drinks',
                                                                                         'services')
            serializer = serializers.WeddingBookingSerializer(bookings, many=True)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class WeddingHallViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = WeddingHall.objects.filter(is_active=True).order_by('name').prefetch_related('weddinghallprice_set')
    serializer_class = serializers.WeddingHallSerializer
    pagination_class = paginators.HallPaginator

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
            q = q.strip()
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

        event_date = request.query_params.get('event_date')
        time = request.query_params.get('time')
        is_weekend_event = False

        if event_date:
            event_date = datetime.fromisoformat(event_date)
            is_weekend_event = event_date.weekday() >= 5  # Xác định nếu là cuối tuần
        else:
            event_date = timezone.now()
            is_weekend_event = event_date.weekday() >= 5

        price_queryset = WeddingHallPrice.objects.filter(
            wedding_hall__in=queryset,
            is_weekend=is_weekend_event
        )
        if time:
            price_queryset = price_queryset.filter(time=time)

        price_data = serializers.WeddingHallPriceSerializer(price_queryset, many=True).data
        price_dict = {}
        for price in price_data:
            hall_id = price['wedding_hall']
            if hall_id not in price_dict:
                price_dict[hall_id] = []
            price_dict[hall_id].append(price)

        # Gán giá vào từng sảnh
        for hall in serializer.data:
            hall['prices'] = price_dict.get(hall['id'], [])

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='check-booking-status')
    def check_booking_status(self, request):
        rental_date = request.query_params.get('rental_date')
        time_of_day = request.query_params.get('time_of_day')
        wedding_hall_id = request.query_params.get('wedding_hall_id')

        if not rental_date or not time_of_day or not wedding_hall_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            rental_date = datetime.fromisoformat(rental_date)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            wedding_hall = WeddingHall.objects.get(id=wedding_hall_id)
        except WeddingHall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        is_booked = WeddingBooking.objects.filter(
            wedding_hall=wedding_hall,
            rental_date=rental_date,
            time_of_day=time_of_day
        ).exists()

        return Response({
            "wedding_hall_id": wedding_hall_id,
            "rental_date": rental_date.date(),
            "time_of_day": time_of_day,
            "is_booked": is_booked
        }, status=status.HTTP_200_OK)


#  Có phân trang
# class WeddingHallViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
#     queryset = WeddingHall.objects.filter(is_active=True).order_by('name')
#     serializer_class = serializers.WeddingHallSerializer
#     pagination_class = paginators.HallPaginator
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         if self.action.__eq__('list'):
#             q = self.request.query_params.get('q', None)
#             min_price = self.request.query_params.get('min_price', None)
#             max_price = self.request.query_params.get('max_price', None)
#             time = self.request.query_params.get('time', None)
#             event_date = self.request.query_params.get('event_date', None)
#
#             # Xử lý kiểm tra ngày
#             if event_date:
#                 event_date = datetime.fromisoformat(event_date)
#             else:
#                 event_date = timezone.now()
#
#             is_weekend = event_date.weekday() >= 5  # T7 và CN
#
#             # Lọc theo tên
#             if q:
#                 q = q.strip()
#                 queryset = queryset.filter(name__icontains=q)
#
#             # Lọc theo buổi
#             if time:
#                 queryset = queryset.filter(weddinghallprice__time=time)
#
#             # Lọc theo min_price
#             if min_price is not None:
#                 queryset = queryset.filter(
#                     weddinghallprice__price__gte=min_price,
#                     weddinghallprice__is_weekend=is_weekend,
#                     weddinghallprice__time=time
#                 ).distinct()
#
#             # Lọc theo max_price
#             if max_price is not None:
#                 queryset = queryset.filter(
#                     weddinghallprice__price__lte=max_price,
#                     weddinghallprice__is_weekend=is_weekend,
#                     weddinghallprice__time=time
#                 ).distinct()
#
#             return queryset.distinct()
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         page = self.paginate_queryset(queryset)
#
#         if page is not None:
#             serializer = self.get_serializer(page, many=True) # Sử dụng khi có phân trang
#
#             # Lấy giá cho từng sảnh tiệc
#             for hall in serializer.data:
#                 event_date = request.query_params.get('event_date')
#                 time = request.query_params.get('time')
#                 is_weekend_event = False
#
#                 if event_date:
#                     event_date = datetime.fromisoformat(event_date)
#                     is_weekend_event = event_date.weekday() >= 5  # Xác định nếu là cuối tuần
#                 else:
#                     event_date = timezone.now()
#                     is_weekend_event = event_date.weekday() >= 5
#
#                 # Lọc giá theo buổi và ngày
#                 if time:
#                     hall['prices'] = serializers.WeddingHallPriceSerializer(
#                         WeddingHallPrice.objects.filter(
#                             wedding_hall=hall['id'],
#                             is_weekend=is_weekend_event,
#                             time=time
#                         ),
#                         many=True
#                     ).data
#                 else:
#                     # Nếu không có time, lấy tất cả giá cho ngày hiện tại
#                     hall['prices'] = serializers.WeddingHallPriceSerializer(
#                         WeddingHallPrice.objects.filter(
#                             wedding_hall=hall['id'],
#                             is_weekend=is_weekend_event
#                         ),
#                         many=True
#                     ).data
#
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


class WeddingHallImageViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = WeddingHallImage.objects.all()
    serializer_class = serializers.WeddingHallImageSerializer


class WeddingHallPriceViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = WeddingHallPrice.objects.all()
    serializer_class = serializers.WeddingHallPriceSerializer

    def get_queryset(self):
        queryset = self.queryset

        # Lấy các tham số từ request
        hall_id = self.request.query_params.get('hall_id')
        time_of_day = self.request.query_params.get('time_of_day')
        event_date = self.request.query_params.get('event_date')

        # Nếu không có tham số nào, trả về tất cả giá
        if not hall_id and not time_of_day and not event_date:
            return queryset

        # Kiểm tra nếu có cung cấp hall_id
        if hall_id:
            queryset = queryset.filter(wedding_hall_id=hall_id)

        # Kiểm tra nếu có cung cấp time_of_day
        if time_of_day:
            queryset = queryset.filter(time=time_of_day)

        # Kiểm tra nếu có cung cấp event_date
        if event_date:
            try:
                event_date = timezone.datetime.fromisoformat(event_date)
                is_weekend = event_date.weekday() >= 5  # 5 là thứ Bảy, 6 là Chủ Nhật
                queryset = queryset.filter(is_weekend=is_weekend)
            except ValueError:
                return WeddingHallPrice.objects.none()  # Trả về queryset rỗng nếu ngày không hợp lệ

        return queryset


class EventTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = EventType.objects.all()
    serializer_class = serializers.EventTypeSerializer


class ServiceViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True).order_by('id')
    serializer_class = serializers.ServiceSerializer
    pagination_class = paginators.FoodDrinkServicePaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')

            if q:
                q = q.strip()
                queryset = queryset.filter(name__icontains=q)

            order_by = self.request.query_params.get('order_by')
            if order_by:
                if order_by == 'asc':
                    queryset = queryset.order_by('price')
                elif order_by == 'desc':
                    queryset = queryset.order_by('-price')

        return queryset


class DrinkViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Drink.objects.filter(is_active=True).order_by('id')
    serializer_class = serializers.DrinkSerializer
    pagination_class = paginators.FoodDrinkServicePaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                q = q.strip()
                queryset = queryset.filter(name__icontains=q)

            order_by = self.request.query_params.get('order_by')
            if order_by:
                if order_by == 'asc':
                    queryset = queryset.order_by('price')
                elif order_by == 'desc':
                    queryset = queryset.order_by('-price')

        return queryset


class FoodTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = FoodType.objects.all().order_by('id')
    serializer_class = serializers.FoodTypeSerializer


class FoodViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Food.objects.filter(is_active=True).order_by('id')
    serializer_class = serializers.FoodSerializer
    pagination_class = paginators.FoodDrinkServicePaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                q = q.strip()
                queryset = queryset.filter(name__icontains=q)

            foodtype_id = self.request.query_params.get('foodtype_id')
            if foodtype_id:
                queryset = queryset.filter(food_type_id=foodtype_id)

            order_by = self.request.query_params.get('order_by')
            if order_by:
                if order_by == 'asc':
                    queryset = queryset.order_by('price')
                elif order_by == 'desc':
                    queryset = queryset.order_by('-price')

        return queryset


class WeddingBookingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    queryset = WeddingBooking.objects.all()
    serializer_class = serializers.WeddingBookingSerializer

    def create(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        table_quantity = request.data.get('table_quantity')
        rental_date = request.data.get('rental_date')
        time_of_day = request.data.get('time_of_day')
        payment_method = request.data.get('payment_method')
        payment_status = request.data.get('payment_status')
        total_price = request.data.get('total_price')
        wedding_hall = request.data.get('wedding_hall')
        customer = request.data.get('customer')
        event_type = request.data.get('event_type')

        foods = request.data.get("foods", [])
        drinks = request.data.get("drinks", [])
        services = request.data.get("services", [])

        if not name or not table_quantity or not rental_date or not payment_method or not payment_status or not total_price:
            return Response(data='Thiếu thông tin bắt buộc', status=status.HTTP_400_BAD_REQUEST)

        try:
            wedding_booking = WeddingBooking.objects.create(
                name=name,
                description=description,
                table_quantity=table_quantity,
                rental_date=rental_date,
                time_of_day=time_of_day,
                payment_method=payment_method,
                payment_status=payment_status,
                total_price=total_price,
                wedding_hall=WeddingHall.objects.get(id=wedding_hall),
                customer=Customer.objects.get(user_id=customer),
                event_type=EventType.objects.get(id=event_type)
            )

            for food in foods:
                food_instance = Food.objects.get(id=food['food'])
                food_booking_detail = FoodBookingDetail.objects.create(
                    food=food_instance,
                    quantity=food['quantity'],
                    wedding_booking=wedding_booking
                )
                serializers.FoodBookingDetailSerializer(food_booking_detail)

            for drink in drinks:
                drink_instance = Drink.objects.get(id=drink['drink'])
                drink_booking_detail = DrinkBookingDetail.objects.create(
                    drink=drink_instance,
                    quantity=drink['quantity'],
                    wedding_booking=wedding_booking
                )
                serializers.DrinkBookingDetailSerializer(drink_booking_detail)

            for service in services:
                service_instance = Service.objects.get(id=service['service'])
                service_booking_detail = ServiceBookingDetail.objects.create(
                    service=service_instance,
                    quantity=service['quantity'],
                    wedding_booking=wedding_booking
                )
                serializers.ServiceBookingDetailSerializer(service_booking_detail)

            serialized_wedding_booking = serializers.WeddingBookingSerializer(wedding_booking)
            return Response(serialized_wedding_booking.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request):
        wedding_booking_id = request.data.get('wedding_booking_id')

        if wedding_booking_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            customer = Customer.objects.get(user=request.user)
            serializer.save(customer=customer, wedding_booking_id=wedding_booking_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Momo
@csrf_exempt
def payment_view(request: HttpRequest):
    accessKey = 'F8BBA842ECF85'
    secretKey = 'K951B6PE1waDMi640xX08PD3vg6EkVlz'
    orderInfo = 'Pay with MoMo'
    partnerCode = 'MOMO'
    redirectUrl = 'https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b'
    ipnUrl = 'https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b'
    requestType = "payWithMethod"
    amount = request.headers.get('amount', '')  # Lấy amount từ header (Lấy giá từ header)
    orderId = partnerCode + str(int(time.time() * 1000))
    requestId = orderId
    extraData = ''
    orderGroupId = ''
    autoCapture = True
    autoCapture = True
    lang = 'vi'

    # Tạo chuỗi signature
    rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
    signature = hmac.new(secretKey.encode(), rawSignature.encode(), hashlib.sha256).hexdigest()

    # Tạo request body
    data = {
        "partnerCode": partnerCode,
        "partnerName": "Test",
        "storeId": "MomoTestStore",
        "requestId": requestId,
        "amount": amount,
        "orderId": orderId,
        "orderInfo": orderInfo,
        "redirectUrl": redirectUrl,
        "ipnUrl": ipnUrl,
        "lang": lang,
        "requestType": requestType,
        "autoCapture": autoCapture,
        "extraData": extraData,
        "orderGroupId": orderGroupId,
        "signature": signature
    }

    # Gửi request đến MoMo
    response = requests.post('https://test-payment.momo.vn/v2/gateway/api/create', json=data)
    response_data = response.json()
    pay_url = response_data.get('payUrl')

    return JsonResponse(response_data)


# ZaloPay
config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
}


@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        # Lấy thông tin từ yêu cầu của người dùng
        amount = request.headers.get('amount', '')  # Lấy amount từ header (lấy giá từ header)
        transID = random.randrange(1000000)
        # Xây dựng yêu cầu thanh toán
        order = {
            "app_id": config["app_id"],
            "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID),  # mã giao dich có định dạng yyMMdd_xxxx
            "app_user": "user123",
            "app_time": int(round(time.time() * 1000)),  # miliseconds
            "embed_data": json.dumps({}),
            "item": json.dumps([{}]),
            "amount": amount,
            "description": "Thanh Toán Đơn Đặt Tiệc #" + str(transID),
            "bank_code": "",
        }

        # Tạo chuỗi dữ liệu và mã hóa HMAC
        data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"],
                                             order["amount"], order["app_time"], order["embed_data"], order["item"])
        order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

        # Gửi yêu cầu đến ZaloPay API
        try:
            response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
            result = json.loads(response.read())
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"Lỗi": str(e)})
    else:
        return JsonResponse({"Lỗi": "Chỉ yêu cầu POST được cho phép"})
