# Generated by Django 4.2 on 2025-01-27 05:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('vendor_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
