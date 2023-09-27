from django.db import models

# Create your models here.
class Attendance(models.Model):
    EmpCode = models.CharField(max_length=50)
    Date = models.CharField(max_length=50)
    Status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.EmpCode