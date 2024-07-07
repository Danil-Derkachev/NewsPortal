from django.contrib import admin
from modeltranslation.admin import TranslationAdmin  # импортируем модель амдинки (вспоминаем модуль про переопределение стандартных админ-инструментов)

from .models import *


def nullfy_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)


nullfy_rating.short_description = 'Обнулить рейтинг' # описание для более понятного представления в админ панеле задаётся, как будто это объект


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'type', 'datetime', 'title', 'rating', 'is_popular')  # если вам нужны только какие-то конкретные поля
    list_filter = ('author', 'rating')  # добавляем примитивные фильтры в нашу админку
    search_fields = ('title', )  # тут всё очень похоже на фильтры из запросов в базу
    actions = [nullfy_rating]  # добавляем действия в список


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCategory._meta.get_fields()]


class CommentAdmin(admin.ModelAdmin):  #FIXME AttributeError at /admin/my_news_portal/comment/  Unable to lookup 'likedcomment' on Comment or CommentAdmin
    list_display = [field.name for field in Comment._meta.get_fields()]


class SubscriberAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Subscriber._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения


class LikedCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LikedComment._meta.get_fields()]


class DislikedCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DislikedComment._meta.get_fields()]


class LikedPostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LikedPost._meta.get_fields()]


class DislikedPostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DislikedPost._meta.get_fields()]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(LikedComment, LikedCommentAdmin)
admin.site.register(DislikedComment, DislikedCommentAdmin)
admin.site.register(LikedPost, LikedPostAdmin)
admin.site.register(DislikedPost, DislikedPostAdmin)
