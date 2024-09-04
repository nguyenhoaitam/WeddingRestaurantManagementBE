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
    Service, Drink, FoodType, Food, WeddingBooking, Feedback, Customer
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
            user_data['user_role'] = user_role.id
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


class WeddingHallViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = WeddingHall.objects.filter(is_active=True).order_by('name')
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
                event_date = timezone.now()
                is_weekend_event = event_date.weekday() >= 5

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

            order_by = self.request.query_params.get('order_by')
            if order_by:
                if order_by == 'asc':
                    queryset = queryset.order_by('price')
                elif order_by == 'desc':
                    queryset = queryset.order_by('-price')

        return queryset


class FoodTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = FoodType.objects.all()
    serializer_class = serializers.FoodTypeSerializer

    # @action(methods=['get'], detail=True, url_path='foods')
    # def get_foods(self, request, pk=None):
    #     try:
    #         food_type = FoodType.objects.get(pk=pk)
    #     except FoodType.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    #     foods = food_type.food_set.filter(is_active=True)
    #
    #     q = request.query_params.get('q')
    #     if q:
    #         foods = foods.filter(name__icontains=q)
    #
    #     serialized_foods = serializers.FoodSerializer(foods, many=True, context={"request": request})
    #     return Response(serialized_foods.data, status=status.HTTP_200_OK)


class FoodViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Food.objects.filter(is_active=True)
    serializer_class = serializers.FoodSerializer
    # pagination_class = paginators.FoodPaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
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
    parser_classes = [parsers.MultiPartParser]


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
    # amount = request.headers.get('amount', '')  # Lấy amount từ header  (Số tiền)
    amount = '5000'
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
        amount = request.headers.get('amount', '')  # Lấy amount từ header (lấy giá)
        transID = random.randrange(1000000)
        # Xây dựng yêu cầu thanh toán
        order = {
            "app_id": config["app_id"],
            "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID),  # mã giao dich có định dạng yyMMdd_xxxx
            "app_user": "user123",
            "app_time": int(round(time.time() * 1000)),  # miliseconds
            "embed_data": json.dumps({}),
            "item": json.dumps([{}]),
            # "amount": amount,
            "amount": '50000',
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
            return JsonResponse({"error": str(e)})
    else:
        return JsonResponse({"error": "Only POST requests are allowed"})