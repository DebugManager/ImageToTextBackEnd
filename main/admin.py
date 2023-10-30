from django.contrib import admin

from main.models import CompanyDoc, Company





@admin.register(Company)
class Company(admin.ModelAdmin):
    pass


@admin.register(CompanyDoc)
class CompanyDocs(admin.ModelAdmin):
    pass
