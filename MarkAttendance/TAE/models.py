from django.db import models

# Create your models here.
class TAESheet(models.Model):
    docfile = models.FileField(upload_to='documents/TAE')

class MasterTAE(models.Model):
    User_Name = models.CharField(max_length=200)
    Location = models.CharField(max_length=200)
    Date = models.CharField(max_length=200)
    Project = models.CharField(max_length=200)
    Project_Task = models.CharField(max_length=200)
    Activity = models.CharField(max_length=200)
    Role = models.CharField(max_length=200)
    Internal_Note = models.CharField(max_length=200)
    Bill_Rate = models.CharField(max_length=200)
    Bill_Hrs = models.CharField(max_length=200)
    NB_Hrs = models.CharField(max_length=200)
    Total_Hrs = models.CharField(max_length=200)
    Revenue_Reason = models.CharField(max_length=200)