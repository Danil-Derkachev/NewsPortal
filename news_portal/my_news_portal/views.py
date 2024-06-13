import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache

from .filters import PostFilter
from .forms import NewsForm
from .models import *
from .tasks import *


logger = logging.getLogger(__name__)


class NewsList(LoginRequiredMixin, ListView):
    """ Отображение всех новостей и статей """
    model = Post
    ordering = '-datetime'  # Сортировка по дате (не по времени)
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10


    def get_queryset(self):
        logger.error("Hello! I'm error in your app. Enjoy:)")
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['categories'] = Category.objects.all()
        context['all_news'] = Post.objects.all()
        return context


class OneNewsDetail(DetailView):
    """ Отображение отдельно взятой новости или статьи """
    model = Post
    template_name = 'one_news.html'
    context_object_name = 'one_news'


    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'one_news-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'one_news-{self.kwargs["pk"]}', obj)
        return obj


class NewsCreate(PermissionRequiredMixin, CreateView):
    """ Создание новости """
    permission_required = ('my_news_portal.add_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'create_news.html'


    def form_valid(self, form):
        post = form.save()#(commit=False)
        post.type = 'NE'
        send_email_to_subscribed_users.apply_async([post.pk])
        return super().form_valid(form)


class NewsEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """ Редактирование новости """
    permission_required = ('my_news_portal.change_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_news.html'


class NewsDelete(DeleteView):
    """ Удаление новости """
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('news_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    """ Создание статьи """
    permission_required = ('my_news_portal.add_post',)
    form_class = NewsForm
    model = Post
    template_name = 'create_article.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'
        return super().form_valid(form)


class ArticleEdit(PermissionRequiredMixin, UpdateView):
    """ Редактирование статьи """
    permission_required = ('my_news_portal.change_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_article.html'


class ArticleDelete(DeleteView):
    """ Удаление статьи """
    model = Post
    template_name = 'delete_article.html'
    success_url = reverse_lazy('news_list')


def subscribe_to_category(request):
    """Подписка на категорию"""
    category_obj = Category.objects.get(name=request.POST['category'])
    sub_obj = Subscriber.objects.filter(user=request.user, category=category_obj)
    if not sub_obj:
        Subscriber.objects.create(user=request.user, category=category_obj)
        return redirect('news_list')
    else:
        return redirect('news_list')


def unsubscribe_from_category(request):
    """Отписка от категории"""
    category_obj = Category.objects.get(name=request.POST['category'])
    sub_obj = Subscriber.objects.filter(user=request.user, category=category_obj)
    if sub_obj:
        Subscriber.objects.filter(user=request.user, category=category_obj).delete()
        return redirect('news_list')
    else:
        return redirect('news_list')


def like_post(request, **kwargs):
    """Повышает рейтинг новости или статьи на единицу"""
    for name, value in kwargs.items():
        post = Post.objects.get(id=value)
        post.like()
    return redirect(post.get_absolute_url())


def dislike_post(request, **kwargs):
    """Понижает рейтинг новости или статьи на единицу"""
    for name, value in kwargs.items():
        post = Post.objects.get(id=value)
        post.dislike()
    return redirect(post.get_absolute_url())
