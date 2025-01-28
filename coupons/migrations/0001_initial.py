# Generated by Django 5.1.5 on 2025-01-28 06:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField()),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('coupon', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='discount_rule', to='coupons.coupon')),
            ],
        ),
        migrations.CreateModel(
            name='MinPurchaseCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_purchase_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('coin_reward', models.IntegerField(blank=True, null=True)),
                ('coupon', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='min_purchase_rule', to='coupons.coupon')),
            ],
        ),
    ]
