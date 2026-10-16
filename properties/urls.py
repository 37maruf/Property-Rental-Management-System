from django.urls import path

from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='list'),
    path('properties/<int:pk>/', views.property_detail, name='detail'),
    path('owner/properties/add/', views.property_create, name='create'),
    path('owner/properties/<int:pk>/edit/', views.property_update, name='update'),
    path('owner/properties/<int:pk>/delete/', views.property_delete, name='delete'),
]
