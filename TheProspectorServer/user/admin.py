from django.contrib import admin

# Register your models here.
from user.models import UnlockedLevel, LevelCompletionStat, LevelStar

admin.site.register(UnlockedLevel)
admin.site.register(LevelCompletionStat)
admin.site.register(LevelStar)