from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

# the model field called `property` shadows the builtin inside class bodies
_property = property


class RentalRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]

    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE,
                                 related_name='rental_requests')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='rental_requests')
    message = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        ordering = ['-request_date']
        constraints = [
            # DB-level rule: one pending request per tenant per property
            models.UniqueConstraint(
                fields=['property', 'tenant'],
                condition=Q(status='pending'),
                name='unique_pending_request_per_tenant_property',
            ),
        ]

    def __str__(self):
        return f'{self.tenant} -> {self.property} ({self.status})'

    @_property
    def is_pending(self):
        return self.status == self.PENDING


class Review(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE,
                                 related_name='reviews')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['property', 'tenant'],
                                    name='one_review_per_tenant_per_property'),
        ]

    def __str__(self):
        return f'{self.tenant} rated {self.property} {self.rating}/5'

    @_property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
