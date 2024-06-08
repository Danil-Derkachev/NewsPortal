from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache

from .filters import PostFilter
from .forms import NewsForm
from .models import *
from .tasks import *


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-datetime'  # Сортировка по дате (не по времени)
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
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
    permission_required = ('my_news_portal.change_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_news.html'


class NewsDelete(DeleteView):
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('news_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('my_news_portal.add_post',)
    form_class = NewsForm
    model = Post
    template_name = 'create_article.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'
        return super().form_valid(form)


class ArticleEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('my_news_portal.change_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_article.html'


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'delete_article.html'
    success_url = reverse_lazy('news_list')


def news_subscribe(request):
    #sub = Subscriber.objects.filter(user=request.user).first()
    if request.method == 'POST':
        #if not sub:
            category_object = Category.objects.get(name=request.POST['category'])
            Subscriber.objects.create(user=request.user, category=category_object)
            return redirect('news_list')
        #else:
            #redirect('news_list')
    else:
        return redirect('news_list')
