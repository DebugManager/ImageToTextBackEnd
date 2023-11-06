from django.contrib import admin

# Register your models here.
from user.models import CustomUser, Feature


@admin.register(CustomUser)
class MyUser(admin.ModelAdmin):
    pass


@admin.register(Feature)
class Feature(admin.ModelAdmin):
    pass
