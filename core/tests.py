from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class AuthFlowTests(TestCase):
    def test_registration_creates_user_and_redirects_to_login(self):
        url = reverse('registrar')
        payload = {
            'username': 'nuevo_usuario',
            'password1': 'SecretoFuerte123',
            'password2': 'SecretoFuerte123',
            'email': 'nuevo@ejemplo.com',
            'rol': User.ROL_LECTOR,
        }
        resp = self.client.post(url, payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())
        # Debe mostrar la página de login después del registro
        self.assertContains(resp, 'Ingresar')

    def test_login_with_username_redirects_correctly(self):
        user = User.objects.create_user(
            username='user1', email='user1@ejemplo.com', password='ClaveSegura123', rol=User.ROL_LECTOR
        )
        url = reverse('login')
        resp = self.client.post(url, {'username': 'user1', 'password': 'ClaveSegura123'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Redirige al listado de libros para lector
        self.assertContains(resp, 'Libros')

    def test_login_with_email_redirects_correctly(self):
        user = User.objects.create_user(
            username='user2', email='user2@ejemplo.com', password='ClaveSegura123', rol=User.ROL_LECTOR
        )
        url = reverse('login')
        resp = self.client.post(url, {'username': 'user2@ejemplo.com', 'password': 'ClaveSegura123'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Libros')

    def test_db_health_endpoint_ok(self):
        # Asegura que el endpoint de salud responde 200 en entorno de prueba
        url = reverse('db_health')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('status', resp.json())
