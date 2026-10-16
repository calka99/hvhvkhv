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


class AccountPasswordChangeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='password-owner',
            email='password-owner@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(self.user)

    def test_authenticated_user_can_change_password(self):
        response = self.client.post(
            reverse('account-change-password'),
            {
                'current_password': 'StrongPass123!',
                'new_password': 'NewStrongPass456!',
                'confirm_password': 'NewStrongPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass456!'))

    def test_password_change_rejects_incorrect_current_password(self):
        response = self.client.post(
            reverse('account-change-password'),
            {
                'current_password': 'WrongPass123!',
                'new_password': 'NewStrongPass456!',
                'confirm_password': 'NewStrongPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('StrongPass123!'))

    def test_password_change_rejects_mismatched_confirmation(self):
        response = self.client.post(
            reverse('account-change-password'),
            {
                'current_password': 'StrongPass123!',
                'new_password': 'NewStrongPass456!',
                'confirm_password': 'DifferentPass789!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_password_change_rejects_password_that_fails_django_validators(self):
        response = self.client.post(
            reverse('account-change-password'),
            {
                'current_password': 'StrongPass123!',
                'new_password': 'password',
                'confirm_password': 'password',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)
