from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class TestMyNewsPortal(TestCase):
    def test_news_list(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


    def test_create_news(self):
        response = self.client.get(reverse('create_news'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
