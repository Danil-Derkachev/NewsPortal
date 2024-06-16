from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache


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
        return f'{self.user}'


class Category(SomeBaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Subscriber(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.category}'


class Post(SomeBaseModel):
    article = 'AR'
    news = 'NE'

    TYPES = [
        (article, 'Article'),
        (news, 'News')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPES, default=article)
    datetime = models.DateField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self, value=1):
        self.rating += value
        self.save()

    def dislike(self, value=1):
        self.rating -= value
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    @property
    def is_popular(self):
        return self.rating > 0

    def __str__(self):
        return f'{self.id}: {self.title}'

    def get_absolute_url(self):
        return reverse('detail_post', kwargs={'pk': self.id})  # После создания новости или статьи вернёт на созданную страницу

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'detail_post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(SomeBaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post}: {self.category}'


class LikedPost(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.post}'


class DislikedPost(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.post}'


class Comment(SomeBaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)

    def like(self, value=1):
        self.rating += value
        self.save()

    def dislike(self, value=1):
        self.rating -= value
        self.save()

    def __str__(self):
        return f'{self.user}: {self.text}'

    def get_absolute_url(self):
        return reverse('detail_comment', kwargs={'pk': self.id})


class LikedComment(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.comment}'


class DislikedComment(SomeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}: {self.comment}'
