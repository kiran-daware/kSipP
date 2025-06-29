from django.db import models

class AppConfig(models.Model):
    # Unique identifier to ensure we have a singleton config
    key = models.CharField(max_length=100, unique=True, default='main')

    # XML form fields
    select_uac = models.CharField(max_length=100, default='uac_basic.xml')
    select_uas = models.CharField(max_length=100, default='uas_basic.xml')

    # IP config form fields
    uac_remote = models.GenericIPAddressField(default='1.1.1.1')
    uac_remote_port = models.PositiveIntegerField(default=5060)
    uas_remote = models.GenericIPAddressField(default='2.2.2.2')
    uas_remote_port = models.PositiveIntegerField(default=5060)
    local_addr = models.GenericIPAddressField(default='3.3.3.3')
    src_port_uac = models.PositiveIntegerField(default=5060)
    src_port_uas = models.PositiveIntegerField(default=5062)
    protocol_uac = models.CharField(max_length=10, choices=[('u1', 'UDP'), ('tn', 'TCP')], default='u1')
    protocol_uas = models.CharField(max_length=10, choices=[('u1', 'UDP'), ('tn', 'TCP')], default='u1')

    # More options form fields
    called_party_number = models.CharField(max_length=30, blank=True)
    calling_party_number = models.CharField(max_length=30, blank=True)
    total_no_of_calls = models.PositiveIntegerField(default=1)
    cps = models.PositiveIntegerField(default=1, null=True)
    stun_server = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"AppConfig ({self.key})"
