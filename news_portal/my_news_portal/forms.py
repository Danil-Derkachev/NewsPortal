from django import forms

from .models import Post


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['datetime', 'author', 'categories', 'title', 'text']
