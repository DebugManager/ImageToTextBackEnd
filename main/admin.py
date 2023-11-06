from django.contrib import admin

from main.models import CompanyDoc, Company, Plan


@admin.register(Plan)
class Plan(admin.ModelAdmin):
    pass


@admin.register(Company)
class Company(admin.ModelAdmin):
    pass


@admin.register(CompanyDoc)
class CompanyDocs(admin.ModelAdmin):
    pass
