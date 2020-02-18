from django.contrib import admin

from whatsappwrap.models import Instance, WebhookUrl

admin.site.register(Instance)
admin.site.register(WebhookUrl)
