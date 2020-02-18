from django.conf import settings
from django.db.models import Model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Instance(Model):
    token = models.OneToOneField(Token, on_delete=models.CASCADE)
    phone = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    profile_path = models.CharField(max_length=255, blank=True, null=True)
    is_loggedin = models.BooleanField()
    autoconnect = models.BooleanField()

    def __str__(self):
        return "{} / {}".format(self.name, self.phone)


class WebhookUrl(Model):
    url = models.CharField(max_length=255)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)