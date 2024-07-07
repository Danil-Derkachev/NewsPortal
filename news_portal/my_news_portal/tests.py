from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import *


class TestMyNewsPortal(APITestCase):
    def setUp(self):
        Category.objects.create(name='Спорт')
        Category.objects.create(name='Наука')
        User.objects.create(username='JohnDoe')
        user_1 = User.objects.get(username='JohnDoe')
        Author.objects.create(user=user_1)

    def test_list_posts(self):
        response = self.client.get(reverse('list_posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_news(self):
        url = reverse('create_news')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        user_1 = User.objects.get(username='JohnDoe')
        author_1 = Author.objects.get(user=user_1)
        all_categories = Category.objects.all()
        data = {'author': author_1, 'categories': all_categories, 'type': 'NE', 'title': 'test_title', 'text': 'test_text'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_article(self):
        response = self.client.get(reverse('create_article'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
