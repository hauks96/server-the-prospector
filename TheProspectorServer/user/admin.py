from django.contrib import admin

# Register your models here.
from user.models import LevelProgress, LevelCompletionStats

admin.site.register(LevelProgress)
admin.site.register(LevelCompletionStats)