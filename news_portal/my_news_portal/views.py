import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache

from .filters import PostFilter
from .forms import NewsForm, CommentForm, CommentEditForm
from .models import *
from .tasks import *


logger = logging.getLogger(__name__)


class NewsList(LoginRequiredMixin, ListView):
    """ Список всех новостей и статей """
    model = Post
    ordering = '-datetime'  # Сортировка по дате (не по времени)
    template_name = 'my_news_portal/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10


    def get_queryset(self):
        # logger.debug("Hello! I'm debug in your app. Enjoy:)")
        # logger.info("Hello! I'm info in your app. Enjoy:)")
        # logger.warning("Hello! I'm warning in your app. Enjoy:)")
        # logger.error("Hello! I'm error in your app. Enjoy:)")
        # logger.critical("Hello! I'm critical in your app. Enjoy:)")

        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['categories'] = Category.objects.all()
        context['all_news'] = Post.objects.all()
        context['user_subscribes'] = Subscriber.objects.filter(user=self.request.user).values_list('category__name', flat=True)  # flat=True заменяет [(Спорт,), (Наука,)] на [Спорт, Наука]
        return context


class OneNewsDetail(DetailView):
    """ Отдельно взятая новость или статья """
    model = Post
    template_name = 'my_news_portal/one_news.html'
    context_object_name = 'one_news'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'one_news-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'one_news-{self.kwargs["pk"]}', obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.kwargs['pk']).order_by('-rating')
        return context


class NewsCreate(PermissionRequiredMixin, CreateView):
    """ Создание новости """
    permission_required = ('my_news_portal.add_post',)
    # Указываем нашу разработанную форму
    form_class = NewsForm
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'my_news_portal/create_news.html'

    def form_valid(self, form):
        post = form.save()#(commit=False)
        post.type = 'NE'
        send_email_to_subscribed_users.apply_async([post.pk])
        return super().form_valid(form)


class NewsEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """ Редактирование новости """
    permission_required = ('my_news_portal.change_post',)
    form_class = NewsForm
    model = Post
    template_name = 'my_news_portal/edit_news.html'


class NewsDelete(DeleteView):
    """ Удаление новости """
    model = Post
    template_name = 'my_news_portal/delete_news.html'
    success_url = reverse_lazy('news_list')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    """ Создание статьи """
    permission_required = ('my_news_portal.add_post',)
    form_class = NewsForm
    model = Post
    template_name = 'my_news_portal/create_article.html'

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
    template_name = 'my_news_portal/edit_article.html'


class ArticleDelete(DeleteView):
    """ Удаление статьи """
    model = Post
    template_name = 'my_news_portal/delete_article.html'
    success_url = reverse_lazy('news_list')


class CommentCreate(CreateView):
    """ Создание комментария к новости или статье """
    form_class = CommentForm
    model = Comment
    template_name = 'my_news_portal/create_comment.html'

    def get_success_url(self):
        """Перенаправление после успешного создания комментария"""
        success_url = reverse('one_news', args=[self.request.POST["post"]])
        return success_url


class CommentDetail(DeleteView):
    """Отдельно взятый комментарий"""
    model = Comment


class CommentEdit(UpdateView):
    """Редактирование комментария"""
    form_class = CommentEditForm
    model = Comment
    template_name = 'my_news_portal/edit_comment.html'

    def get_success_url(self):
        """Перенаправление после успешного редактирования комментария"""
        success_url = reverse('one_news', args=[self.request.POST["post"]])
        return success_url


class CommentDelete(DeleteView):
    """ Удаление комментария """
    model = Comment
    template_name = 'my_news_portal/delete_comment.html'

    def get_success_url(self):
        """Перенаправление после успешного удаления комментария"""
        success_url = reverse('one_news', args=[self.request.GET["post_id"]])
        return success_url


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
    post = Post.objects.get(id=kwargs['pk'])
    post.like()
    return redirect(post.get_absolute_url())


def dislike_post(request, **kwargs):
    """Понижает рейтинг новости или статьи на единицу"""
    post = Post.objects.get(id=kwargs['pk'])
    post.dislike()
    return redirect(post.get_absolute_url())


def like_comment(request, **kwargs):
    """Повышает рейтинг комментария на единицу"""
    comment_obj = Comment.objects.get(id=request.POST['comment_id'])
    comment_obj.like()
    return redirect('one_news', comment_obj.post.id)


def dislike_comment(request, **kwargs):
    """Понижает рейтинг комментария на единицу"""
    comment_obj = Comment.objects.get(id=request.POST['comment_id'])
    comment_obj.dislike()
    return redirect('one_news', comment_obj.post.id)
