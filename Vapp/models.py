from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import datetime
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

import secrets

from datetime import datetime, timedelta

class Store(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True)
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    description = models.TextField()
    logo = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vendor'], name='unique_store_per_user')
        ]


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, editable=True)
   
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.PositiveIntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CustomOrder(models.Model):
    class OrderChoices(models.TextChoices):
        cancelled = "Cancelled", "Cancelled"
        completed = "Completed", "Completed"
        pending = "Pending", "Pending"

    class AcceptChoices(models.TextChoices):
        yes = "Yes", "Yes"
        no = "No", "No"
        pending = "Pending", "Pending"


    class DeliveryChoices(models.TextChoices):
        processing = "Processing", "Processing"
        pending = "Pending", "Pending"
        shipped = "Shipped", "Shipped"
        delivered = "Delivered", "Delivered"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ordered_items')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='orders')
    specifications = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    counter_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    shipped_date = models.DateField(blank=True, null=True)
    accept_status = models.CharField(max_length=15, choices=AcceptChoices.choices, default=AcceptChoices.pending)
    delivery_status = models.CharField(max_length=15, choices=DeliveryChoices.choices, default=DeliveryChoices.pending)
    order_status = models.CharField(max_length=15, choices=OrderChoices.choices, default=OrderChoices.pending)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} from {self.store.name}"

class Messages(models.Model):
    message = models.TextField()
    order = models.ForeignKey(CustomOrder, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        ordering = ("-timestamp",)

    def save(self, *args, **kwargs):
        if not self.sender:
            self.sender = self.order.user
        if not self.receiver:
            self.receiver = self.order.store.vendor.user
        super().save(*args, **kwargs)
