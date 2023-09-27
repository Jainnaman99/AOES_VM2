from django.db import models

# Create your models here.
class Resource(models.Model):
    Role_choices = [
        ('Software Engineer','Software Engineer'),
        ('Senior Software Engineer','Senior Software Engineer'),
        ('Senior Quality Engineer','Senior Quality Engineer (3.2)'),
        ('Lead Software Engineer','Lead Software Engineer (3.3)'),
        ('Lead Quality Engineer','Lead Quality Engineer (3.3)'),
        ('Engineering Lead','Engineering Lead (5.1)'),
        ('Engineering Lead - Quality','Engineering Lead - Quality (5.1)'),
        ('Senior Engineering Lead','Senior Engineering Lead (5.2)'),
        ('Senior Engineering Lead - Quality','Senior Engineering Lead - Quality (5.2)'),
        ('Project Lead','Project Lead (5.3)'),
        ('Project Lead - Quality','Project Lead - Quality (5.3)'),
        ('Architect','Architect (7.1)'),
        ('Senior Architect','Senior Architect'),
        ('Contract Consultant','Contract Consultant'),           
    ]
    # Grade_choices = [
    #     ('3.0','3.0'),
    #     ('3.1','3.1'),
    #     ('3.2','3.2'),
    #     ('3.3','3.3'),
    #     ('5.1','5.1'),
    #     ('5.2','5.2'),
    #     ('5.3','5.3'),
    #     ('7.1','7.1'),
    #     ('7.2','7.2'),
    # ]
    Sow_choices = [
        
        ('Engineer (SDE1)','Engineer (SDE1)'),
        ('Senior Engineer (SDE2)','Senior Engineer (SDE2)'),
        ('Senior Engineer (SDE3)','Senior Engineer (SDE3)'),
        ('Quality Engineer (SDET1)','Quality Engineer (SDET1)'),
        ('QE Automation','QE Automation'),
        ('QE Automation Lead','QE Automation Lead'),
        ('Quality Lead (SDE2)','Quality Lead (SDE2)'),
        ('Business Analyst','Business Analyst')
    ]
    Project_choices = [
        ('SG:SFDF','SG:SFDF'),
        ('JOSYS','JOSYS')
    ]
    Location_choices=[
        ('Pune','Pune'),
        ('Bengaluru','Bengaluru'),
        ('Nagpur','Nagpur'),
        ('Bengaluru SEZ','Bengaluru SEZ'),
    ]

    EmpCode = models.PositiveSmallIntegerField() # add validator 

    EmpName = models.CharField(max_length=100)

    SowRoles = models.CharField(max_length=50, choices=Sow_choices, blank=False)

    Role = models.CharField(max_length=100, choices=Role_choices, blank=False)

    Project = models.CharField(max_length=100,choices=Project_choices, default=" ", blank=False)

    Location = models.CharField(max_length=100,choices=Location_choices, blank=False)

    Billed = models.CharField(max_length=100,choices=[('Yes','Yes'),('No','No')] , default="Yes", blank=False)

    Status = models.CharField(max_length=100, choices=[('Active','Active'), ('Inactive','Inactive')],default='Active', blank=False)
    def __str__(self):
        return self.EmpName
