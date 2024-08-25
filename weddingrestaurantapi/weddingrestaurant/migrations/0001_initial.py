# Generated by Django 5.1 on 2024-08-25 06:16

import ckeditor.fields
import cloudinary.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar', cloudinary.models.CloudinaryField(max_length=255, null=True)),
                ('phone', models.CharField(max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Drink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('image', cloudinary.models.CloudinaryField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('image', cloudinary.models.CloudinaryField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
                ('is_vagetarian', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FoodType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('image', cloudinary.models.CloudinaryField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeddingHall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('capacity', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('full_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=150)),
                ('gender', models.CharField(max_length=15)),
                ('dob', models.DateField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('full_name', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=30)),
                ('salary', models.FloatField()),
                ('address', models.CharField(max_length=150)),
                ('gender', models.CharField(max_length=15)),
                ('dob', models.DateField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DrinkBookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('unit', models.CharField(max_length=50)),
                ('drink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.drink')),
            ],
        ),
        migrations.CreateModel(
            name='FoodBookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.food')),
            ],
        ),
        migrations.AddField(
            model_name='food',
            name='food_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.foodtype'),
        ),
        migrations.CreateModel(
            name='ServiceBookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.service')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='user_role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='weddingrestaurant.userrole'),
        ),
        migrations.CreateModel(
            name='WeddingBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('table_quantity', models.IntegerField()),
                ('rental_date', models.DateField()),
                ('method', models.CharField(max_length=50)),
                ('payment_status', models.CharField(max_length=50)),
                ('total_price', models.FloatField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('drinks', models.ManyToManyField(through='weddingrestaurant.DrinkBookingDetail', to='weddingrestaurant.drink')),
                ('event_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='weddingrestaurant.eventtype')),
                ('foods', models.ManyToManyField(through='weddingrestaurant.FoodBookingDetail', to='weddingrestaurant.food')),
                ('services', models.ManyToManyField(through='weddingrestaurant.ServiceBookingDetail', to='weddingrestaurant.service')),
            ],
        ),
        migrations.AddField(
            model_name='servicebookingdetail',
            name='wedding_booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='weddingrestaurant.weddingbooking'),
        ),
        migrations.AddField(
            model_name='foodbookingdetail',
            name='wedding_booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='weddingrestaurant.weddingbooking'),
        ),
        migrations.AddField(
            model_name='drinkbookingdetail',
            name='wedding_booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='weddingrestaurant.weddingbooking'),
        ),
        migrations.CreateModel(
            name='WeddingHallImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', cloudinary.models.CloudinaryField(max_length=255)),
                ('wedding_hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.weddinghall')),
            ],
        ),
        migrations.CreateModel(
            name='WeddingHallPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(choices=[(1, 'Morning'), (2, 'Noon'), (3, 'Evening')], max_length=20)),
                ('is_weekend', models.BooleanField(default=False)),
                ('is_holiday', models.BooleanField(default=False)),
                ('price', models.FloatField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('wedding_hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.weddinghall')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('rating', models.IntegerField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.customer')),
            ],
        ),
    ]
