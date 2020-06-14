from django.db import models

# Create your models here.
class CriterionsAlternativesAmount(models.Model):
    criterions = models.IntegerField()
    alternatives = models.IntegerField()