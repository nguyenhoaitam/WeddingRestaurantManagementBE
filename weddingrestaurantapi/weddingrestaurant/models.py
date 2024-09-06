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

    def has_role(self, required_role):
        return self.user_role == required_role

    def save(self, *args, **kwargs):
        if not self.pk and self.is_superuser:
            admin_role, created = UserRole.objects.get_or_create(name='admin')
            self.user_role = admin_role
        super().save(*args, **kwargs)


class Staff(models.Model):  # Nhân viên
    GENDER_CHOICE = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ')
    ]
    full_name = models.CharField(max_length=100, null=False)
    position = models.CharField(max_length=30, null=False)
    salary = models.FloatField()
    address = models.CharField(max_length=150, null=False)
    gender = models.CharField(max_length=15, null=False, choices=GENDER_CHOICE)
    dob = models.DateField(null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.full_name


class Customer(models.Model):  # Khách hàng
    GENDER_CHOICE = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ')
    ]
    full_name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=150, null=True, blank=True)
    gender = models.CharField(max_length=15, null=True, blank=True, choices=GENDER_CHOICE)
    dob = models.DateField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.full_name


class WeddingHall(models.Model):  # Sảnh tiệc
    name = models.CharField(max_length=100, null=False)
    description = RichTextField(null=True, blank=True)
    capacity = models.IntegerField(null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_images(self):
        return self.weddinghallimage_set.all()


class WeddingHallImage(models.Model):  # Ảnh của sảnh tiệc
    path = CloudinaryField()
    wedding_hall = models.ForeignKey(WeddingHall, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ảnh của sảnh {self.wedding_hall}"


class WeddingHallPrice(models.Model):  # Giá của sảnh tiệc
    TIME_CHOICES = [
        ('Sáng', 'Sáng'),
        ('Trưa', 'Trưa'),
        ('Tối', 'Tối'),
    ]
    time = models.CharField(max_length=20, null=False, choices=TIME_CHOICES)
    is_weekend = models.BooleanField(default=False)
    price = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    wedding_hall = models.ForeignKey(WeddingHall, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.price:.2f}"


class EventType(models.Model):  # Loại tiệc
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class BaseModel(models.Model):
    price = models.FloatField()
    description = RichTextField(null=True, blank=True)
    image = CloudinaryField()
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Service(BaseModel):  # Dịch vụ
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class Drink(BaseModel):  # Nước uống
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class FoodType(models.Model):  # Loại đồ ăn
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class Food(BaseModel):  # Đồ ăn
    name = models.CharField(max_length=50, null=False)
    is_vegetarian = models.BooleanField(default=False)
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class WeddingBooking(models.Model):  # Đơn đặt tiệc
    name = models.CharField(max_length=50, null=False)
    description = RichTextField(null=True, blank=True)
    table_quantity = models.IntegerField()
    rental_date = models.DateField()
    payment_method = models.CharField(max_length=50, null=False)
    payment_status = models.CharField(max_length=50)
    total_price = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)
    wedding_hall = models.ForeignKey(WeddingHall, on_delete=models.SET_NULL, null=True)
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    foods = models.ManyToManyField('Food', through='FoodBookingDetail')
    drinks = models.ManyToManyField('Drink', through='DrinkBookingDetail')
    services = models.ManyToManyField('Service', through='ServiceBookingDetail')

    def __str__(self):
        return self.name


class Feedback(models.Model):  # Phản hồi của khách hàng
    RATING_CHOICES = [
        (1, 'Rất tệ'),
        (2, 'Tệ'),
        (3, 'Bình thường'),
        (4, 'Tốt'),
        (5, 'Rất tốt'),
    ]

    content = RichTextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class ServiceBookingDetail(models.Model):  # Chi tiết dịch vụ của đơn đặt tiệc
    quantity = models.IntegerField(null=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)


class DrinkBookingDetail(models.Model):  # Chi tiết nước uống của đơn đặt tiệc
    quantity = models.IntegerField(null=False)
    unit = models.CharField(max_length=50)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)


class FoodBookingDetail(models.Model): # Chi tiết đồ ăn của đơn đặt tiệc
    quantity = models.IntegerField(null=False)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    wedding_booking = models.ForeignKey(WeddingBooking, on_delete=models.PROTECT)
