from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User

from main.models import CompanyDoc, MyUser, Company


@admin.register(MyUser)
class MyUser(admin.ModelAdmin):
    pass

@admin.register(Company)
class Company(admin.ModelAdmin):
    pass


@admin.register(CompanyDoc)
class CompanyDocs(admin.ModelAdmin):
    pass
