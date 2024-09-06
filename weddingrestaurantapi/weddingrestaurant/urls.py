from django.urls import path, include
from rest_framework import routers
from weddingrestaurant import views

r = routers.DefaultRouter()

r.register('user_roles', views.UserRoleViewSet, 'user_roles')
r.register('users', views.UserViewSet, 'users')
r.register('staffs', views.StaffViewSet, 'staffs')
r.register('customers', views.CustomerViewSet, 'customers')
r.register('wedding_halls', views.WeddingHallViewSet, 'wedding_halls')
r.register('wedding_hall_images', views.WeddingHallImageViewSet, 'wedding_hall_images')
r.register('wedding_hall_prices', views.WeddingHallPriceViewSet, 'wedding_hall_prices')
r.register('event_types', views.EventTypeViewSet, 'event_types')
r.register('services', views.ServiceViewSet, 'services')
r.register('drinks', views.DrinkViewSet, 'drinks')
r.register('food_types', views.FoodTypeViewSet, 'food_type')
r.register('foods', views.FoodViewSet, 'foods')
r.register('wedding_bookings', views.WeddingBookingViewSet, 'wedding_bookings')
r.register('feedbacks', views.FeedbackViewSet, 'feedbacks')

urlpatterns = [
    path('', include(r.urls)),
    path('momo/payment/', views.payment_view, name='payment'),
    path('zalopay/payment/', views.create_payment, name='zalopay'),
]
