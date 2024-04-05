from django.db import models
from django.contrib.auth.models import User

class trains(models.Model):
    train_number = models.IntegerField(null=False, default=0)
    source=models.CharField(max_length=50)
    destination=models.CharField(max_length=50)
    total_seats=models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(trains, on_delete=models.CASCADE)
    seat_count = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True) 

