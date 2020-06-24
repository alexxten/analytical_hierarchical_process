from django.db import models

# Create your models here.
class CriterionsAlternativesAmount(models.Model):
    criterions = models.IntegerField()
    alternatives = models.IntegerField()

class CriterionsComparison(models.Model):
    fk_id = models.IntegerField()
    c1 = models.IntegerField()
    c2 = models.IntegerField()
    c1c2_value = models.FloatField()

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