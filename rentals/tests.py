from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from properties.models import Property

from .models import RentalRequest, Review


class RentalRulesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner1', 'o1@x.com', 'pass12345', role='owner')
        self.owner2 = User.objects.create_user('owner2', 'o2@x.com', 'pass12345', role='owner')
        self.tenant = User.objects.create_user('tenant1', 't1@x.com', 'pass12345', role='tenant')
        self.prop = Property.objects.create(
            title='Flat', description='Nice', property_type='apartment', location='Dhaka',
            monthly_rent=10000, bedrooms=2, bathrooms=1, owner=self.owner)

    def _send(self, msg='I would like to rent this.'):
        return self.client.post(reverse('rentals:send_request', args=[self.prop.pk]), {'message': msg})

    def test_anonymous_cannot_request(self):
        r = self._send()
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r.url)
        self.assertEqual(RentalRequest.objects.count(), 0)

    def test_tenant_can_request_once_while_pending(self):
        self.client.login(username='tenant1', password='pass12345')
        self._send()
        self._send()
        self.assertEqual(RentalRequest.objects.count(), 1)

    def test_owner_cannot_request_own_property(self):
        self.client.login(username='owner1', password='pass12345')
        self._send()
        self.assertEqual(RentalRequest.objects.count(), 0)

    def test_only_owner_can_accept(self):
        req = RentalRequest.objects.create(property=self.prop, tenant=self.tenant, message='hello there!')
        self.client.login(username='owner2', password='pass12345')
        r = self.client.post(reverse('rentals:accept_request', args=[req.pk]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'pending')
        self.client.login(username='owner1', password='pass12345')
        self.client.post(reverse('rentals:accept_request', args=[req.pk]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

    def test_tenant_can_cancel_pending(self):
        req = RentalRequest.objects.create(property=self.prop, tenant=self.tenant, message='hello there!')
        self.client.login(username='tenant1', password='pass12345')
        self.client.post(reverse('rentals:cancel_request', args=[req.pk]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'cancelled')

    def test_review_needs_accepted_request_and_only_once(self):
        self.client.login(username='tenant1', password='pass12345')
        url = reverse('rentals:add_review', args=[self.prop.pk])
        self.client.post(url, {'rating': 5, 'comment': 'Great'})
        self.assertEqual(Review.objects.count(), 0)
        RentalRequest.objects.create(property=self.prop, tenant=self.tenant,
                                     message='hello there!', status='accepted')
        self.client.post(url, {'rating': 5, 'comment': 'Great'})
        self.client.post(url, {'rating': 4, 'comment': 'Again'})
        self.assertEqual(Review.objects.count(), 1)

    def test_owner_cannot_edit_or_delete_others_property(self):
        self.client.login(username='owner2', password='pass12345')
        r = self.client.post(reverse('properties:update', args=[self.prop.pk]), {})
        self.assertEqual(r.status_code, 403)
        r = self.client.post(reverse('properties:delete', args=[self.prop.pk]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Property.objects.filter(pk=self.prop.pk).exists())

    def test_middleware_blocks_wrong_role(self):
        self.client.login(username='tenant1', password='pass12345')
        r = self.client.get(reverse('rentals:owner_dashboard'))
        self.assertEqual(r.status_code, 302)

    def test_search_filters(self):
        Property.objects.create(title='Big', description='x', property_type='house', location='Barisal',
                                monthly_rent=50000, bedrooms=4, bathrooms=2, owner=self.owner)
        r = self.client.get(reverse('properties:list'), {'location': 'bar', 'min_rent': 20000})
        self.assertContains(r, 'Big')
        self.assertNotContains(r, 'Flat')
