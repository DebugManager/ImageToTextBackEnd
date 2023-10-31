from django.db import models


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


class CompanyDoc(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number_of_docs = models.IntegerField()
    number_of_pg = models.IntegerField()
    time_added = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()


class SupportPost(models.Model):
    collum_title = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField()



# class Feedback(models.Model):
#     uset_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     text = models.TextField()


# class Affiliate(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     email = models.EmailField()
#     # password # todo
#     promotion_plan = models.TextField()
#     twitter = models.CharField(max_length=255)
#     instagram = models.CharField(max_length=255)
#     tiktok = models.CharField(max_length=255)
#     linkedin = models.CharField(max_length=255)
#     facebook = models.CharField(max_length=255)
#     paypal_email = models.EmailField()
#     btc_adress = models.CharField(max_length=255)
