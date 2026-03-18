from django.contrib import admin
from .models import User, UserDetail, Address, RolePermission

# Register your models here.
admin.site.register(User)
admin.site.register(UserDetail)
admin.site.register(Address)
admin.site.register(RolePermission)
