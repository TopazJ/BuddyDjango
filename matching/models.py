import uuid
from django.db import models
from django.contrib.auth import models as auth_models

# Create your models here.


class Client(models.Model):
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512, null=True)
    phone = models.CharField(max_length=12, null=False, unique=True)


class Volunteer(Client):
    user = models.OneToOneField(auth_models.User, on_delete=models.CASCADE)
    province = models.CharField(max_length=2)
    city = models.CharField(max_length=256)
    available = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)


class ClientInterest(models.Model):
    interest = models.CharField(max_length=64)
    rating = models.FloatField()
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)


class VolunteerInterest(models.Model):
    interest = models.CharField(max_length=64)
    owner = models.ForeignKey(Volunteer, on_delete=models.CASCADE)


class Call(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, null=False, related_name='vol')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False, related_name='cli')
    rating = models.FloatField(default=0)
    counter = models.IntegerField(default=0)
