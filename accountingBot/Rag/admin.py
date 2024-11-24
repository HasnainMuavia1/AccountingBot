from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Params)
admin.site.register(models.ChatHistory)

admin.site.register(models.ChatSession)