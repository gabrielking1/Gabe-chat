# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Store, Product, CustomOrder, Category, Messages
from unfold.admin import ModelAdmin


admin.site.unregister(User)


@admin.register(Store)  
class StoreAdmin(ModelAdmin):
    pass

@admin.register(Product)    
class ProductAdmin(ModelAdmin):
    pass

@admin.register(CustomOrder)
class CustomOrderAdmin(ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass

@admin.register(Messages)
class MessagesAdmin(ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass