from django.contrib import admin

from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'location', 'monthly_rent', 'bedrooms',
                    'bathrooms', 'is_available', 'owner', 'created_at')
    list_filter = ('property_type', 'is_available', 'created_at')
    search_fields = ('title', 'location', 'owner__username')
    list_editable = ('is_available',)
    autocomplete_fields = ('owner',)
    date_hierarchy = 'created_at'
