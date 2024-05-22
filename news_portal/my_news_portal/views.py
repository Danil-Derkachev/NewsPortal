from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .filters import PostFilter
from .forms import NewsForm
from .models import *


class NewsList(ListView):
    model = Post
    ordering = '-datetime'
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class OneNewsDetail(DetailView):
    model = Post
    template_name = 'one_news.html'
    context_object_name = 'one_news'


class NewsCreate(CreateView):
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'create_news.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NE'
        return super().form_valid(form)


class NewsEdit(UpdateView):
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_news.html'


class NewsDelete(DeleteView):
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('news_list')


class ArticleCreate(CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'create_article.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'
        return super().form_valid(form)


class ArticleEdit(UpdateView):
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_article.html'


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'delete_article.html'
    success_url = reverse_lazy('news_list')

