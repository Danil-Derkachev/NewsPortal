from django import forms

from .models import Post, Category


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'categories', 'title', 'text']
