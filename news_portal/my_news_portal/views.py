import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache
from django.utils.translation import gettext as _

from .filters import PostFilter
from .forms import *
from .models import *
from .tasks import *


logger = logging.getLogger(__name__)


class PostsList(ListView):
    """Список всех публикаций"""
    model = Post
    ordering = '-datetime'
    template_name = 'my_news_portal/list_posts.html'
    context_object_name = 'list_posts'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Post.objects.select_related('author__user').all()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['categories'] = Category.objects.all()
        context['posts'] = Post.objects.select_related('author__user').all()
        if self.request.user.is_authenticated:
            context['user_subscribes'] = Subscriber.objects.select_related('user', 'category').filter(
                user=self.request.user).values_list('category__id', flat=True)  # flat=True заменяет [(Спорт,), (Наука,)] на [Спорт, Наука]
        return context


class PostDetail(DetailView):
    """Отдельно взятая публикация"""
    queryset = Post.objects.select_related('author__user').all()
    model = Post
    template_name = 'my_news_portal/detail_post.html'
    context_object_name = 'detail_post'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'detail_post-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.
        if not obj:  # если объекта нет в кэше, то получаем его и записываем в кэш
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'detail_post-{self.kwargs["pk"]}', obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.select_related('post', 'user').filter(post=self.kwargs['pk']
                                                                                    ).order_by('-rating')
        return context


class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание новости"""
    permission_required = ('my_news_portal.add_post',)
    form_class = PostForm  # Указываем нашу разработанную форму
    model = Post
    template_name = 'my_news_portal/create_news.html'  # и новый шаблон, в котором используется форма

    def form_valid(self, form):
        """Заполнение оставшихся полей формы отправленной пользователем"""
        post = form.save(commit=False)
        post.type = 'NE'
        post.author = Author.objects.get(user=self.request.user)
        send_email_to_subscribed_users.apply_async([post.pk])  # Отправка почты
        return super().form_valid(form)


class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование публикации"""
    permission_required = ('my_news_portal.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'my_news_portal/edit_post.html'


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление публикации"""
    model = Post
    template_name = 'my_news_portal/delete_post.html'
    success_url = reverse_lazy('list_posts')


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание статьи"""
    permission_required = ('my_news_portal.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'my_news_portal/create_article.html'

    def form_valid(self, form):
        """Заполнение оставшихся полей формы отправленной пользователем"""
        post = form.save(commit=False)
        post.type = 'AR'
        post.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)


class CommentCreate(LoginRequiredMixin, CreateView):
    """Создание комментария к публикации"""
    form_class = CommentForm
    model = Comment
    template_name = 'my_news_portal/create_comment.html'

    def form_valid(self, form):
        """Заполнение оставшихся полей отправленной пользователем формы"""
        comment = form.save(commit=False)
        comment.post = Post.objects.get(id=self.request.GET['post_id'])
        comment.user = User.objects.get(id=self.request.user.id)
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправление после успешного создания комментария"""
        success_url = reverse('detail_post', args=[self.request.GET["post_id"]])
        return success_url


class CommentEdit(LoginRequiredMixin, UpdateView):
    """Редактирование комментария"""
    form_class = CommentForm
    model = Comment
    template_name = 'my_news_portal/edit_comment.html'

    def get_success_url(self):
        """Перенаправление после успешного редактирования комментария"""
        success_url = reverse('detail_post', args=[self.request.GET["post_id"]])
        return success_url


class CommentDelete(LoginRequiredMixin, DeleteView):
    """Удаление комментария"""
    model = Comment
    template_name = 'my_news_portal/delete_comment.html'

    def get_success_url(self):
        """Перенаправление после успешного удаления комментария"""
        success_url = reverse('detail_post', args=[self.request.GET["post_id"]])
        return success_url


@login_required
def subscribe_to_category(request, **kwargs):
    """Подписка на категорию"""
    sub_obj = Subscriber.objects.filter(user=request.user, category=kwargs['pk'])
    if not sub_obj:
        category_obj = Category.objects.get(id=kwargs['pk'])
        Subscriber.objects.create(user=request.user, category=category_obj)
        return redirect('list_posts')
    else:
        return redirect('list_posts')


@login_required
def unsubscribe_from_category(request, **kwargs):
    """Отписка от категории"""
    sub_obj = Subscriber.objects.filter(user=request.user, category=kwargs['pk'])
    if sub_obj:
        category_obj = Category.objects.get(id=kwargs['pk'])
        Subscriber.objects.filter(user=request.user, category=category_obj).delete()
        return redirect('list_posts')
    else:
        return redirect('list_posts')


@login_required
def like_post(request, **kwargs):
    """Повышает рейтинг публикации на единицу"""
    post_obj = Post.objects.get(id=kwargs['pk'])
    user_liked_post = LikedPost.objects.filter(user=request.user.id, post=post_obj)
    user_disliked_post = DislikedPost.objects.filter(user=request.user.id, post=post_obj)
    if not user_liked_post and not user_disliked_post:  # Если пользователь ещё не лайкал и не дизлайкал публикацию
        post_obj.like()
        LikedPost.objects.create(user=request.user, post=post_obj)
    elif user_liked_post:  # Если уже лайкал
        pass
    elif not user_liked_post and user_disliked_post:  # Если уже дизлайкал
        post_obj.like(2)
        LikedPost.objects.create(user=request.user, post=post_obj)
        DislikedPost.objects.filter(user=request.user, post=post_obj).delete()
    post_obj.author.update_rating()
    return redirect('detail_post', post_obj.id)


@login_required
def dislike_post(request, **kwargs):
    """Понижает рейтинг публикации на единицу"""
    post_obj = Post.objects.get(id=kwargs['pk'])
    user_liked_post = LikedPost.objects.filter(user=request.user.id, post=post_obj)
    user_disliked_post = DislikedPost.objects.filter(user=request.user.id, post=post_obj)
    if not user_liked_post and not user_disliked_post:  # Если пользователь ещё не лайкал и не дизлайкал публикацию
        post_obj.dislike()
        DislikedPost.objects.create(user=request.user, post=post_obj)
    elif user_disliked_post:  # Если уже дизлайкал
        pass
    elif user_liked_post and not user_disliked_post:  # Если уже лайкал
        post_obj.dislike(2)
        DislikedPost.objects.create(user=request.user, post=post_obj)
        LikedPost.objects.filter(user=request.user, post=post_obj).delete()
    post_obj.author.update_rating()
    return redirect('detail_post', post_obj.id)


@login_required
def like_comment(request, **kwargs):
    """Повышает рейтинг комментария на единицу"""
    comment_obj = Comment.objects.get(id=kwargs['pk'])
    user_liked_comment = LikedComment.objects.filter(user=request.user.id, comment=comment_obj)
    user_disliked_comment = DislikedComment.objects.filter(user=request.user.id, comment=comment_obj)
    if not user_liked_comment and not user_disliked_comment:  # Если пользователь ещё не лайкал и не дизлайкал комментарий
        comment_obj.like()
        LikedComment.objects.create(user=request.user, comment=comment_obj)
    elif user_liked_comment:  # Если уже лайкал
        pass
    elif not user_liked_comment and user_disliked_comment:  # Если уже дизлайкал
        comment_obj.like(2)
        LikedComment.objects.create(user=request.user, comment=comment_obj)
        DislikedComment.objects.filter(user=request.user, comment=comment_obj).delete()
    comment_creator_is_author = Author.objects.get(user=comment_obj.user)
    if comment_creator_is_author:
        comment_creator_is_author.update_rating()
    return redirect('detail_post', comment_obj.post.id)


@login_required
def dislike_comment(request, **kwargs):
    """Понижает рейтинг комментария на единицу"""
    comment_obj = Comment.objects.get(id=kwargs['pk'])
    user_liked_comment = LikedComment.objects.filter(user=request.user.id, comment=comment_obj)
    user_disliked_comment = DislikedComment.objects.filter(user=request.user.id, comment=comment_obj)
    if not user_liked_comment and not user_disliked_comment:  # Если пользователь ещё не лайкал и не дизлайкал комментарий
        comment_obj.dislike()
        DislikedComment.objects.create(user=request.user, comment=comment_obj)
    elif user_disliked_comment:  # Если уже дизлайкал
        pass
    elif user_liked_comment and not user_disliked_comment:  # Если уже лайкал
        comment_obj.dislike(2)
        DislikedComment.objects.create(user=request.user, comment=comment_obj)
        LikedComment.objects.filter(user=request.user, comment=comment_obj).delete()
    comment_creator_is_author = Author.objects.get(user=comment_obj.user)
    if comment_creator_is_author:
        comment_creator_is_author.update_rating()
    return redirect('detail_post', comment_obj.post.id)
