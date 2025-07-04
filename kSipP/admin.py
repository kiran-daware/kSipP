# admin.py

from django.contrib import admin
from .models import UacAppConfig, UasAppConfig

@admin.register(UacAppConfig)
class UacAppConfigAdmin(admin.ModelAdmin):
    list_display = ('uac_key', 'uac_config_name', 'select_uac', 'uac_remote', 'is_active_config')

@admin.register(UasAppConfig)
class UasAppConfigAdmin(admin.ModelAdmin):
    list_display = ('uas_key', 'uas_config_name', 'select_uas', 'uas_remote', 'uas_remote_port', 'is_active_config')

admin.site.site_header = "kSipP Admin"
admin.site.site_title = "kSipP Admin"
admin.site.index_title = "Welcome to the Admin Interface"
