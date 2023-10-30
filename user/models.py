from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from main.models import Plan, Company
from .managers import CustomUserManager


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
    last_name = models.CharField(max_length=50, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zip_code = models.IntegerField(null=True)
    country = models.CharField(max_length=100, blank=True)
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    joined = models.DateTimeField(default=timezone.now())
    company = models.ManyToManyField(Company, null=True, blank=True)

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
