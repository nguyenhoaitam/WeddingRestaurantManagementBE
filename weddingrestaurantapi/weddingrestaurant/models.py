from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField


class UserRole(models.Model):  # Vai trò (Admin, Nhân viên, Khách hàng)
    name = models.CharField(max_length=30, null=False, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):  # Người dùng
    avatar = CloudinaryField(null=True)
    phone = models.CharField(max_length=10, null=False)
    user_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, null=True)


class Staff(models.Model):  # Nhân viên
    full_name = models.CharField(max_length=100, null=False)
    position = models.CharField(max_length=30, null=False)
    salary = models.FloatField()
    address = models.CharField(max_length=150, null=False)
    gender = models.CharField(max_length=15, null=False)
    dob = models.DateField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.full_name


class Customer(models.Model):  # Khách hàng
    full_name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=150, null=False)
    gender = models.CharField(max_length=15, null=False)
    dob = models.DateField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    content = RichTextField(null=True, blank=True)
    rating = models.IntegerField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class WeddingHall(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = RichTextField(null=True, blank=True)
    capacity = models.IntegerField(null=False)
    is_active = models.BooleanField(default=True)


class WeddingHallImage(models.Model):
    wedding_hall = models.ForeignKey(WeddingHall, on_delete=models.CASCADE)
    image = CloudinaryField()


class WeddingHallPrice(models.Model):
    MORNING = 1
    NOON = 2
    EVENING = 3

    TIME_CHOICES = [
        (MORNING, 'Morning'),
        (NOON, 'Noon'),
        (EVENING, 'Evening'),
    ]
    time = models.CharField(null=False, choices=TIME_CHOICES)
    is_weekend = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    price = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    wedding_hall = models.ForeignKey(WeddingHall, on_delete=models.CASCADE)


class EventType(models.Model):
    name = models.CharField(max_length=50, null=False)


class BaseModel(models.Model):
    price = models.FloatField()
    description = RichTextField(null=True, blank=True)
    image = CloudinaryField()
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Service(BaseModel):
    name = models.CharField(max_length=50, null=False)


class Drink(BaseModel):
    name = models.CharField(max_length=50, null=False)


class FoodType(models.Model):
    name = models.CharField(max_length=50, null=False)


class Food(BaseModel):
    name = models.CharField(max_length=50, null=False)
    is_vagetarian = models.BooleanField(default=False)
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)


class WeddingBooking(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = RichTextField(null=True, blank=True)
    table_quantity = models.IntegerField()
    rental_date = models.DateField()
    method = models.CharField(max_length=50, null=False)
    payment_status = models.CharField(max_length=50)
    total_price = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL)
    foods = models.ManyToManyField('Food', through='FoodBookingDetail')
    drinks = models.ManyToManyField('Drink', through='DrinkBookingDetail')
    services = models.ManyToManyField('Service', through='ServiceBookingDetail')


class ServiceBookingDetail(models.Model):
    quantity = models.IntegerField(null=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)


class DrinkBookingDetail(models.Model):
    quantity = models.IntegerField(null=False)
    unit = models.CharField(max_length=50)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)


class FoodBookingDetail(models.Model):
    quantity = models.IntegerField(null=False)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)
