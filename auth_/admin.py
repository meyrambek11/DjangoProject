from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import Seller,  User, Profile
from api.models import Order, Product, Category, Comment, ShippingAddress, BaseAddress
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_filter = ['gender', 'is_seller', 'location']


admin.site.register(Seller)
admin.site.register(User, UserAdmin)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(ShippingAddress)
admin.site.register(Profile)
