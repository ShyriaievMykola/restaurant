from django.test import Client, SimpleTestCase


class SmokeTests(SimpleTestCase):
    def test_admin_route_is_available(self):
        response = Client().get('/admin/')
        self.assertEqual(response.status_code, 302)