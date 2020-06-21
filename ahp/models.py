from django.db import models

# Create your models here.
class CriterionsAlternativesAmount(models.Model):
    criterions = models.IntegerField()
    alternatives = models.IntegerField()

class CriterionsNames(models.Model):
    fk_id = models.IntegerField()
    cname = models.TextField()

class AlternativesNames(models.Model):
    fk_id = models.IntegerField()
    aname = models.TextField()

class AlternativesCriterionsInfo(models.Model):
    fk_id = models.IntegerField()
    c_id = models.IntegerField()
    a_id = models.IntegerField()
    value = models.FloatField()