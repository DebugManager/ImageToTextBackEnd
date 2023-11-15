import base64
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from main.models import Company
from .managers import CustomUserManager


class Affiliate(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    promotion_plan = models.TextField(blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)
    tiktok = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    paypal_email = models.CharField(max_length=100, blank=True, null=True)
    btc_adress = models.CharField(max_length=255, blank=True, null=True)
    affiliated_users = models.ManyToManyField('CustomUser', related_name='affiliate_membership')
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class AffiliateLink(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    unique_link = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.unique_link:
            # Encode affiliate_id with a UUID
            encoded_id = base64.urlsafe_b64encode(str(self.affiliate.id).encode()).decode()
            self.unique_link = f"{encoded_id}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class AffiliatedUser(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)


class Notification(models.Model):
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True, editable=False)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=50, default="customer")
    customer_id = models.CharField(max_length=100, default="Clear")
    payment_method_id = models.CharField(max_length=100, default=None, blank=True, null=True)
    subscription_id = models.CharField(max_length=100, default=None, blank=True, null=True)

    affiliate_id = models.ForeignKey(Affiliate, on_delete=models.CASCADE, blank=True, null=True)

    objects = CustomUserManager()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zip_code = models.IntegerField(null=True)
    country = models.CharField(max_length=100, blank=True)
    current_plan = models.CharField(max_length=100, null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True)
    company = models.ManyToManyField(Company, null=True, blank=True)

    phone = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default="Succes")

    readed_notification = models.ManyToManyField(Notification, null=True, blank=True)

    # image_url = models.URLField()

    class Meta:
        permissions = [('view', 'Can view specific page'), ('edit', 'Can edit content'), ('comment', 'Can comment'),
                       ('create_new', 'Can create new user')]


class Feature(models.Model):
    name = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)
    voted_users = models.ManyToManyField(CustomUser, through='UserFeatureVote')

    def __str__(self):
        return self.name


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

    website = models.CharField(max_length=100, blank=True, default=True)
    site_code = models.CharField(max_length=100, blank=True, default=True)

    def __str__(self):
        return self.subject


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
