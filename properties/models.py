from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class Property(models.Model):
    APARTMENT = 'apartment'
    HOUSE = 'house'
    ROOM = 'room'
    OFFICE = 'office'
    TYPE_CHOICES = [
        (APARTMENT, 'Apartment'),
        (HOUSE, 'House'),
        (ROOM, 'Room'),
        (OFFICE, 'Office'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=255)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name='Available')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'properties'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('properties:detail', args=[self.pk])

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg']
