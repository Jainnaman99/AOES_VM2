from django.db import models
from django.db.models import F, ExpressionWrapper


class Contract(models.Model):

    CONTRACT_TYPE_CHOICES = [
        ('T&M Price', 'T&M Price'),
        ('Fixed Price', 'Fixed Price')
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ]

    contract_name = models.CharField(max_length=200, blank=False)
    contract_acronym = models.CharField(max_length=200, primary_key=True)

    contract_type = models.CharField(
        max_length=50, choices=CONTRACT_TYPE_CHOICES, blank=False)

    FTE_count = models.IntegerField(blank=False, default=0)

    total_contract_value = models.FloatField(blank=False)

    revenue_projection = models.FloatField(blank=True, default=0)
    revenue_recognised = models.FloatField(blank=True, default=0)

    # computed field
    total_amount_consumed = models.FloatField(
        default=0, editable=False, blank=True, null=False)

    balance = models.FloatField(
        default=0, editable=False, blank=True, null=False)

    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, blank=False)

    def __str__(self):
        return self.contract_acronym

    # def save(self, *args, **kwargs):
    #     self.total_amount_consumed = F(
    #         'revenue_projection') - F('revenue_recognised')

    #     self.balance = F(
    #         'total_contract_value') - F('revenue_recognised')
    #     super(Contract, self).save(*args, **kwargs)
