from django.contrib import admin
from user import models


admin.site.register(models.UserProfile)
admin.site.register(models.Attention)
