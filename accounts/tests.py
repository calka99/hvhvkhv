from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountAuthTests(APITestCase):
    def test_login_with_username_returns_access_and_refresh_tokens(self):
        user = User.objects.create_user(
            username='farmer1',
            email='farmer1@example.com',
            password='StrongPass123!'
        )

        response = self.client.post(
            reverse('account-login'),
            {'username': 'farmer1', 'password': 'StrongPass123!'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['id'], user.id)

    def test_login_with_email_returns_access_and_refresh_tokens(self):
        user = User.objects.create_user(
            username='farmer2',
            email='farmer2@example.com',
            password='StrongPass123!'
        )

        response = self.client.post(
            reverse('account-login'),
            {'username': 'farmer2@example.com', 'password': 'StrongPass123!'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['id'], user.id)

    def test_refresh_endpoint_returns_new_access_token(self):
        login_response = self.client.post(
            reverse('account-login'),
            {'username': 'farmer1', 'password': 'StrongPass123!'},
            format='json',
        )

        response = self.client.post(
            reverse('account-refresh'),
            {'refresh': login_response.data['refresh']},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout_accepts_access_token_without_refresh_token(self):
        user = User.objects.create_user(
            username='farmer4',
            email='farmer4@example.com',
            password='StrongPass123!',
        )
        login_response = self.client.post(
            reverse('account-login'),
            {'username': user.username, 'password': 'StrongPass123!'},
            format='json',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.post(reverse('account-logout'), {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_login_with_invalid_credentials_is_rejected(self):
        User.objects.create_user(
            username='farmer3',
            email='farmer3@example.com',
            password='StrongPass123!'
        )

        response = self.client.post(
            reverse('account-login'),
            {'username': 'farmer3', 'password': 'wrongpassword'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
