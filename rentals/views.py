from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import owner_required, tenant_required
from properties.models import Property

from .forms import RentalRequestForm, ReviewForm
from .models import RentalRequest, Review


def _notify(subject, body, recipient):
    """Bonus: email notification (prints to terminal with the console backend)."""
    if recipient and recipient.email:
        send_mail(subject, body, None, [recipient.email], fail_silently=True)


# ---------- Dashboards ----------

@owner_required
def owner_dashboard(request):
    properties = Property.objects.filter(owner=request.user).annotate(
        pending_count=Count('rental_requests', filter=Q(rental_requests__status='pending')))
    requests_qs = RentalRequest.objects.filter(property__owner=request.user)
    stats = [
        ('Total properties', properties.count(), 'primary'),
        ('Available properties', properties.filter(is_available=True).count(), 'success'),
        ('Total requests', requests_qs.count(), 'dark'),
        ('Pending requests', requests_qs.filter(status='pending').count(), 'warning'),
        ('Accepted requests', requests_qs.filter(status='accepted').count(), 'info'),
    ]
    recent = requests_qs.select_related('property', 'tenant')[:5]
    return render(request, 'rentals/owner_dashboard.html', {
        'stats': stats, 'properties': properties, 'recent_requests': recent})


@tenant_required
def tenant_dashboard(request):
    qs = RentalRequest.objects.filter(tenant=request.user)
    stats = [
        ('Total requests', qs.count(), 'dark'),
        ('Pending', qs.filter(status='pending').count(), 'warning'),
        ('Accepted', qs.filter(status='accepted').count(), 'success'),
        ('Rejected', qs.filter(status='rejected').count(), 'danger'),
    ]
    recent = qs.select_related('property')[:5]
    return render(request, 'rentals/tenant_dashboard.html', {
        'stats': stats, 'recent_requests': recent})


# ---------- Tenant: requests ----------

@tenant_required
@require_POST
def send_request(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    form = RentalRequestForm(request.POST, property=prop, tenant=request.user)
    if form.is_valid():
        rental = form.save(commit=False)
        rental.property = prop
        rental.tenant = request.user
        rental.save()
        _notify(f'New rental request for {prop.title}',
                f'{request.user.username} sent a request:\n\n{rental.message}', prop.owner)
        messages.success(request, 'Your rental request was sent.')
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect('properties:detail', pk=prop.pk)


@tenant_required
def tenant_requests(request):
    qs = RentalRequest.objects.filter(tenant=request.user).select_related('property')
    status = request.GET.get('status')
    if status in dict(RentalRequest.STATUS_CHOICES):
        qs = qs.filter(status=status)
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'rentals/tenant_requests.html', {
        'page_obj': page_obj, 'status': status, 'statuses': RentalRequest.STATUS_CHOICES})


@tenant_required
def tenant_request_detail(request, pk):
    rental = get_object_or_404(RentalRequest.objects.select_related('property', 'property__owner'),
                               pk=pk, tenant=request.user)
    can_review = (rental.status == RentalRequest.ACCEPTED and
                  not Review.objects.filter(property=rental.property, tenant=request.user).exists())
    return render(request, 'rentals/request_detail.html', {'rental': rental, 'can_review': can_review})


@tenant_required
@require_POST
def cancel_request(request, pk):
    rental = get_object_or_404(RentalRequest, pk=pk, tenant=request.user)
    if rental.status != RentalRequest.PENDING:
        messages.error(request, 'Only pending requests can be cancelled.')
    else:
        rental.status = RentalRequest.CANCELLED
        rental.save(update_fields=['status'])
        messages.success(request, 'Request cancelled.')
    return redirect('rentals:tenant_requests')


# ---------- Owner: requests ----------

@owner_required
def owner_requests(request):
    qs = RentalRequest.objects.filter(property__owner=request.user).select_related(
        'property', 'tenant')
    status = request.GET.get('status')
    if status in dict(RentalRequest.STATUS_CHOICES):
        qs = qs.filter(status=status)
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'rentals/owner_requests.html', {
        'page_obj': page_obj, 'status': status, 'statuses': RentalRequest.STATUS_CHOICES})


def _decide(request, pk, new_status):
    rental = get_object_or_404(RentalRequest.objects.select_related('property', 'tenant'), pk=pk)
    if rental.property.owner_id != request.user.id:
        raise PermissionDenied  # only the property owner can decide
    if rental.status != RentalRequest.PENDING:
        messages.error(request, 'This request has already been handled.')
        return redirect('rentals:owner_requests')
    rental.status = new_status
    rental.save(update_fields=['status'])
    _notify(f'Your request for {rental.property.title} was {new_status}',
            f'The owner {new_status} your rental request.', rental.tenant)
    messages.success(request, f'Request {new_status}.')
    return redirect('rentals:owner_requests')


@owner_required
@require_POST
def accept_request(request, pk):
    return _decide(request, pk, RentalRequest.ACCEPTED)


@owner_required
@require_POST
def reject_request(request, pk):
    return _decide(request, pk, RentalRequest.REJECTED)


# ---------- Reviews ----------

@tenant_required
def add_review(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if not RentalRequest.objects.filter(property=prop, tenant=request.user,
                                        status=RentalRequest.ACCEPTED).exists():
        messages.error(request, 'You can review a property only after your request is accepted.')
        return redirect('properties:detail', pk=prop.pk)
    if Review.objects.filter(property=prop, tenant=request.user).exists():
        messages.error(request, 'You have already reviewed this property.')
        return redirect('properties:detail', pk=prop.pk)

    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.property = prop
        review.tenant = request.user
        review.save()
        messages.success(request, 'Thanks for your review!')
        return redirect('properties:detail', pk=prop.pk)
    return render(request, 'rentals/review_form.html', {'form': form, 'property': prop})
