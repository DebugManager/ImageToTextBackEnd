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


class Feature(models.Model):
    name = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)
    voted_users = models.ManyToManyField(CustomUser, through='UserFeatureVote')


class UserFeatureVote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)


class Ticket(models.Model):
    subject = models.CharField(max_length=100)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50)
    image_url = models.URLField(null=True, blank=True)


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)