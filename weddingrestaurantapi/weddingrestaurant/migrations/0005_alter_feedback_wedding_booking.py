# Generated by Django 5.1 on 2024-08-25 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weddingrestaurant', '0004_feedback_wedding_booking_alter_feedback_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='wedding_booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddingrestaurant.weddingbooking'),
        ),
    ]
