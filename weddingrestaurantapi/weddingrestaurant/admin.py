from django.contrib import admin
from weddingrestaurant.models import User, Staff, Customer, Feedback, WeddingHall, WeddingHallImage, WeddingHallPrice, \
    EventType, Service, Drink, FoodType, Food, WeddingBooking
from django.contrib.auth.hashers import make_password
from django.utils.html import mark_safe
from cloudinary.templatetags import cloudinary
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class MyUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'phone', 'user_role']
    search_fields = ['username', 'first_name', 'last_name']
    list_filter = ['user_role']
    readonly_fields = ['user_avatar']

    # Băm mật khẩu khi tạo user
    def save_model(self, request, obj, form, change):
        if not change:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def user_avatar(self, user):
        if user.avatar:
            if type(user.avatar) is cloudinary.CloudinaryResource:
                return mark_safe(f"<img width='100' src='{user.avatar.url}' />")
            return mark_safe(f"<img width='100' src='/static/{user.avatar.name}' />")
        else:
            return "No avatar"


class MyStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'position', 'salary', 'address', 'gender', 'dob']
    search_fields = ['name']


class MyCustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'address', 'gender', 'dob']
    search_fields = ['name']


class WeddingHallForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = WeddingHall
        fields = '__all__'


class MyWeddingHallAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'capacity', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
    form = WeddingHallForm


class MyWeddingHallImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'wedding_hall', 'path']
    list_filter = ['wedding_hall']
    readonly_fields = ['hall_image']

    def hall_image(self, weddinghall):
        if weddinghall.path:
            if type(weddinghall.path) is cloudinary.CloudinaryResource:
                return mark_safe(f"<img width='100' src='{weddinghall.path.url}' />")
            return mark_safe(f"<img width='100' src='/static/{weddinghall.name}' />")
        else:
            return "No image"


class MyWeddingHallPriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'wedding_hall', 'time', 'is_weekend', 'price', 'updated_date']
    list_filter = ['wedding_hall', 'time']


class MyEventTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class MyServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'description', 'image', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
    readonly_fields = ['service_image']

    def service_image(self, service):
        if service.image:
            if type(service.image) is cloudinary.CloudinaryResource:
                return mark_safe(f"<img width='100' src='{service.image.url}' />")
            return mark_safe(f"<img width='100' src='/static/{service.name}' />")
        else:
            return "No image"


class MyDrinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'description', 'image', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
    readonly_fields = ['drink_image']

    def drink_image(self, drink):
        if drink.image:
            if type(drink.image) is cloudinary.CloudinaryResource:
                return mark_safe(f"<img width='100' src='{drink.image.url}' />")
            return mark_safe(f"<img width='100' src='/static/{drink.name}' />")
        else:
            return "No image"


class MyFoodTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


class MyFoodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'food_type', 'is_vegetarian', 'price', 'description', 'image', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
    readonly_fields = ['food_image']

    def food_image(self, food):
        if food.image:
            if type(food.image) is cloudinary.CloudinaryResource:
                return mark_safe(f"<img width='100' src='{food.image.url}' />")
            return mark_safe(f"<img width='100' src='/static/{food.name}' />")
        else:
            return "No image"


class MyWeddingBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'table_quantity', 'rental_date', 'payment_method', 'payment_status',
                    'total_price', 'created_date', 'event_type', 'customer']
    search_fields = ['name', 'description']
    list_filter = ['payment_method', 'payment_status', 'event_type']


class MyFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'wedding_booking', 'content', 'rating', 'created_date', 'updated_date']
    search_fields = ['content']
    list_filter = ['rating']


admin.site.register(User, MyUserAdmin)
admin.site.register(Staff, MyStaffAdmin)
admin.site.register(Customer, MyCustomerAdmin)
admin.site.register(Feedback, MyFeedbackAdmin)
admin.site.register(WeddingHall, MyWeddingHallAdmin)
admin.site.register(WeddingHallImage, MyWeddingHallImageAdmin)
admin.site.register(WeddingHallPrice, MyWeddingHallPriceAdmin)
admin.site.register(EventType, MyEventTypeAdmin)
admin.site.register(Service, MyServiceAdmin)
admin.site.register(Drink, MyDrinkAdmin)
admin.site.register(FoodType, MyFoodTypeAdmin)
admin.site.register(Food, MyFoodAdmin)
admin.site.register(WeddingBooking, MyWeddingBookingAdmin)
