from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.views import logout_view


class LogoutViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='password')

    def test_logout_view_get(self):
        # Create a GET request
        request = self.factory.get(reverse('accounts:logout'))
        request.user = self.user

        # This should fail if the view returns None
        try:
            response = logout_view(request)
            self.assertIsNotNone(response, "The view returned None")
            self.assertEqual(response.status_code, 200)  # Or 302, or 405
        except ValueError as e:
            # Django raises ValueError if view returns None
            self.fail(f"View raised ValueError: {e}")
