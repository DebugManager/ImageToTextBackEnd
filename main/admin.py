from django.contrib import admin

from main.models import CompanyDoc, CustomUser, Company


@admin.register(CustomUser)
class MyUser(admin.ModelAdmin):
    pass


@admin.register(Company)
class Company(admin.ModelAdmin):
    pass


@admin.register(CompanyDoc)
class CompanyDocs(admin.ModelAdmin):
    pass
