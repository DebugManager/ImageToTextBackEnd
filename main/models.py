from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


# User
# Qwerty1234!
# Create your models here.

class Company(models.Model):
    class Meta:
        verbose_name_plural = 'Companies'
    name = models.CharField(max_length=255)
    total_channels = models.IntegerField()
    last_upd = models.DateTimeField(auto_now=True)


class MyUser(AbstractBaseUser):
    username = models.EmailField()
    package = models.IntegerField()
    amount = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField()
    method = models.CharField(max_length=50)
    status = models.IntegerField()


class CompanyDoc(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number_of_docs = models.IntegerField()
    number_of_pg = models.IntegerField()
    time_added = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()
