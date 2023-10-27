from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .managers import CustomUserManager


class Company(models.Model):
    class Meta:
        verbose_name_plural = 'Companies'

    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now=True)


# class Option(models.Model):
#     name = models.CharField(max_length=40, unique=True)
#
#     def __str__(self):
#         return self.name


class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    type = models.CharField(max_length=50, default='Mounth')
    # options = models.ManyToManyField(Option)
    option1 = models.CharField(max_length=50, blank=True)
    option2 = models.CharField(max_length=50, blank=True)
    option3 = models.CharField(max_length=50, blank=True)
    option4 = models.CharField(max_length=50, blank=True)
    option5 = models.CharField(max_length=50, blank=True)
    option6 = models.CharField(max_length=50, blank=True)
    option7 = models.CharField(max_length=50, blank=True)
    option8 = models.CharField(max_length=50, blank=True)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=50, default="customer")

    objects = CustomUserManager()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zip_code = models.IntegerField(null=True)
    country = models.CharField(max_length=100, blank=True)
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    joined = models.DateTimeField(default=timezone.now())  # todo
    company = models.ManyToManyField(Company, null=True, blank=True)  # todo

    # package = models.IntegerField(null=True, blank=True)
    # amount = models.IntegerField()
    ## created_date = models.DateTimeField(auto_now_add=True)
    # paid_date = models.DateTimeField()
    # method = models.CharField(max_length=50)
    # status = models.IntegerField()
    # USERNAME_FIELD = 'email'
    class Meta:
        permissions = [('view', 'Can view specific page'), ('edit', 'Can edit content'), ('comment', 'Can comment'),
                       ('create_new', 'Can create new user')]


class CompanyDoc(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number_of_docs = models.IntegerField()
    number_of_pg = models.IntegerField()
    time_added = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()


class Feature(models.Model):
    name = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

# class Feedback(models.Model):
#     uset_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     text = models.TextField()
