# admin.py

from django.contrib import admin
from .models import AppConfig

@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    list_display = ('key',)

admin.site.site_header = "kSipP Admin"
admin.site.site_title = "kSipP Admin"
admin.site.index_title = "Welcome to the Admin Interface"
