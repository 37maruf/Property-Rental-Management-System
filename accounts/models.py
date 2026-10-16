from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    OWNER = 'owner'
    TENANT = 'tenant'
    ROLE_CHOICES = [
        (OWNER, 'Property Owner'),
        (TENANT, 'Tenant'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=TENANT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    @property
    def is_owner(self):
        return self.role == self.OWNER

    @property
    def is_tenant(self):
        return self.role == self.TENANT

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
