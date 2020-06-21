from django.db import models

# Create your models here.
class CriterionsAlternativesAmount(models.Model):
    criterions = models.IntegerField()
    alternatives = models.IntegerField()

class CriterionsNames(models.Model):
    id = models.IntegerField(primary_key=True)
    cname = models.TextField()

class AlternativesNames(models.Model):
    id = models.IntegerField(primary_key=True)
    aname = models.TextField()