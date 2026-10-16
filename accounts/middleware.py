from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


class RoleAccessMiddleware:
    """
    Guards URL prefixes by role:
      /owner/...  -> only logged-in Property Owners
      /tenant/... -> only logged-in Tenants
    Anonymous users are sent to the login page.
    """

    PROTECTED_PREFIXES = {
        '/owner/': 'owner',
        '/tenant/': 'tenant',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix, role in self.PROTECTED_PREFIXES.items():
            if request.path.startswith(prefix):
                if not request.user.is_authenticated:
                    return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
                if request.user.role != role:
                    messages.error(request, 'You do not have access to that page.')
                    return redirect('properties:list')
        return self.get_response(request)
