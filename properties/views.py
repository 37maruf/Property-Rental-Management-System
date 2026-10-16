from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import owner_required

from .forms import PropertyForm, PropertySearchForm
from .models import Property


def property_list(request):
    properties = Property.objects.filter(is_available=True).select_related('owner')
    form = PropertySearchForm(request.GET or None)

    if form.is_valid():
        data = form.cleaned_data
        if data.get('location'):
            properties = properties.filter(location__icontains=data['location'])
        if data.get('property_type'):
            properties = properties.filter(property_type=data['property_type'])
        if data.get('min_rent') is not None:
            properties = properties.filter(monthly_rent__gte=data['min_rent'])
        if data.get('max_rent') is not None:
            properties = properties.filter(monthly_rent__lte=data['max_rent'])

    page_obj = Paginator(properties, 9).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'properties/list.html', {
        'form': form,
        'page_obj': page_obj,
        'query': params.urlencode(),
    })


def property_detail(request, pk):
    prop = get_object_or_404(Property.objects.select_related('owner'), pk=pk)
    reviews = prop.reviews.select_related('tenant')

    can_request = can_review = False
    existing_request = None
    user = request.user
    if user.is_authenticated and user.is_tenant:
        from rentals.models import RentalRequest, Review
        existing_request = RentalRequest.objects.filter(
            property=prop, tenant=user, status=RentalRequest.PENDING).first()
        can_request = prop.is_available and prop.owner_id != user.id and not existing_request
        has_accepted = RentalRequest.objects.filter(
            property=prop, tenant=user, status=RentalRequest.ACCEPTED).exists()
        can_review = has_accepted and not Review.objects.filter(property=prop, tenant=user).exists()

    from rentals.forms import RentalRequestForm, ReviewForm
    return render(request, 'properties/detail.html', {
        'property': prop,
        'reviews': reviews,
        'avg_rating': prop.average_rating,
        'can_request': can_request,
        'can_review': can_review,
        'existing_request': existing_request,
        'request_form': RentalRequestForm(),
        'review_form': ReviewForm(),
    })


@owner_required
def property_create(request):
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prop = form.save(commit=False)
        prop.owner = request.user
        prop.save()
        messages.success(request, 'Property added.')
        return redirect('rentals:owner_dashboard')
    return render(request, 'properties/form.html', {'form': form, 'title': 'Add property'})


def _get_own_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if prop.owner_id != request.user.id:
        raise PermissionDenied
    return prop


@owner_required
def property_update(request, pk):
    prop = _get_own_property(request, pk)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Property updated.')
        return redirect('rentals:owner_dashboard')
    return render(request, 'properties/form.html', {'form': form, 'title': 'Edit property'})


@owner_required
def property_delete(request, pk):
    prop = _get_own_property(request, pk)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Property deleted.')
        return redirect('rentals:owner_dashboard')
    return render(request, 'properties/confirm_delete.html', {'property': prop})
