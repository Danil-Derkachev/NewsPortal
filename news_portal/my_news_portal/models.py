from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class SomeBaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Author(SomeBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = 0  # Рейтинг всех постов автора
        comments_rating = 0  # Рейтинг всех комментариев автора
        posts_comments_rating = 0  # Рейтинг всех комментариев к постам автора

        posts = Post.objects.filter(author=self)  # Все публикации, текущего автора
        for p in posts:
            posts_rating += p.rating  # Добавляем значение из поля rating
        comments = Comment.objects.filter(user=self.user)  # Все комментарии, текущего автора
        for c in comments:
            comments_rating += c.rating
        posts_comments = Comment.objects.filter(post__author=self)  # Все комментарии к постам текущего автора
        for pc in posts_comments:
            posts_comments_rating += pc.rating

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating  # Обновляем рейтинг автора
        self.save()

    def __str__(self):
        return f'{self.user}: {self.rating}'


class Category(SomeBaseModel):
    name = models.CharField(max_length=255, unique=True)
    #subscribers = models.ManyToManyField(Subscriber, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.name}'#: {self.subscribers}'


class Subscriber(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.category}'


class Post(SomeBaseModel):
    article = 'AR'
    news = 'NE'

    TYPES = [
        (article, 'Статья'),
        (news, 'Новость')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPES, default=article)
    datetime = models.DateField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    def __str__(self):
        return f'{self.title}: {self.text}'

    def get_absolute_url(self):
        return reverse('one_news', kwargs={'pk': self.id})  # После создания новости или статьи вернёт на созданную страницу


class PostCategory(SomeBaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post}: {self.category}'

class Comment(SomeBaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.user}: {self.text}'
