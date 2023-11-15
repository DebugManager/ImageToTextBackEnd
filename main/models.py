from django.db import models


class Company(models.Model):
    class Meta:
        verbose_name_plural = 'Companies'

    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    type = models.CharField(max_length=50, default='Mounth')
    option1 = models.CharField(max_length=50, blank=True)
    option2 = models.CharField(max_length=50, blank=True)
    option3 = models.CharField(max_length=50, blank=True)
    option4 = models.CharField(max_length=50, blank=True)
    option5 = models.CharField(max_length=50, blank=True)
    option6 = models.CharField(max_length=50, blank=True)
    option7 = models.CharField(max_length=50, blank=True)
    option8 = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.name} ({self.type})'


class CompanyDoc(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number_of_docs = models.IntegerField()
    number_of_pg = models.IntegerField()
    time_added = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    def __str__(self):
        return self.name


class SupportPost(models.Model):
    collum_title = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField()
