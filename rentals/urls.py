from django.urls import path

from . import views

app_name = 'rentals'

urlpatterns = [
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/requests/', views.owner_requests, name='owner_requests'),
    path('owner/requests/<int:pk>/accept/', views.accept_request, name='accept_request'),
    path('owner/requests/<int:pk>/reject/', views.reject_request, name='reject_request'),

    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/requests/', views.tenant_requests, name='tenant_requests'),
    path('tenant/requests/<int:pk>/', views.tenant_request_detail, name='request_detail'),
    path('tenant/requests/<int:pk>/cancel/', views.cancel_request, name='cancel_request'),

    path('properties/<int:pk>/request/', views.send_request, name='send_request'),
    path('properties/<int:pk>/review/', views.add_review, name='add_review'),
]
