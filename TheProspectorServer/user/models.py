from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class LevelStar(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username + " : level "+str(self.level) + ", stars "+str(self.stars)


class UnlockedLevel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_level = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + ": " + str(self.current_level)


class LevelCompletionStat(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    restarts = models.IntegerField(default=0)
    time = models.FloatField(default=0.0)
    level = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)

    def __str__(self):
        return "[ user: " + self.user.username + " ], [ level: " + str(self.level) + " ], [ restarts: " + \
               str(self.restarts) + " ], " + "[ time: " + str(self.time) + " ]" + "[ stars: " + str(self.stars)+" ]"
