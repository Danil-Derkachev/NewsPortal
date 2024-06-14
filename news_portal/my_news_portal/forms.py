from django import forms

from .models import Post, Category, Comment


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'categories', 'title', 'text']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'user', 'text']

