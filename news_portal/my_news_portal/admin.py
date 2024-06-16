from django.contrib import admin
from .models import *


def nullfy_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)
nullfy_rating.short_description = 'Обнулить рейтинг' # описание для более понятного представления в админ панеле задаётся, как будто это объект


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
admin.site.register(Author, AuthorAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'type', 'datetime', 'title', 'rating', 'is_popular')  # если вам нужны только какие-то конкретные поля
    list_filter = ('author', 'rating')  # добавляем примитивные фильтры в нашу админку
    search_fields = ('title', )  # тут всё очень похоже на фильтры из запросов в базу
    actions = [nullfy_rating] # добавляем действия в список
admin.site.register(Post, PostAdmin)


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCategory._meta.get_fields()]
admin.site.register(PostCategory, PostCategoryAdmin)


class CommentAdmin(admin.ModelAdmin):  #FIXME AttributeError at /admin/my_news_portal/comment/  Unable to lookup 'likedcomment' on Comment or CommentAdmin
    list_display = [field.name for field in Comment._meta.get_fields()]
admin.site.register(Comment, CommentAdmin)


class SubscriberAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = [field.name for field in Subscriber._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
admin.site.register(Subscriber, SubscriberAdmin)


class LikedCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LikedComment._meta.get_fields()]
admin.site.register(LikedComment, LikedCommentAdmin)


class DislikedCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DislikedComment._meta.get_fields()]
admin.site.register(DislikedComment, DislikedCommentAdmin)


class LikedPostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LikedPost._meta.get_fields()]
admin.site.register(LikedPost, LikedPostAdmin)


class DislikedPostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DislikedPost._meta.get_fields()]
admin.site.register(DislikedPost, DislikedPostAdmin)
