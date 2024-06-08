from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, timedelta

from news_portal import settings
from .models import Subscriber, Post


@shared_task
def send_email_to_subscribed_users(pid):
    post = Post.objects.get(pk=pid)
    categories = Post.objects.filter(pk=pid).values_list('categories__name', flat=True)
    subscribers_emails = set(
        Subscriber.objects.filter(category__name__in=categories).values_list('user__email', flat=True))
    text_content = f'Прочитайте новую новость {post.title}'
    html_content = render_to_string('celery_email.html', {'id': pid, 'title': post.title, 'text': post.text})
    msg = EmailMultiAlternatives(
        subject=post.title,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def send_weekly_email():
    subscribers_emails = set(Subscriber.objects.all().values_list('user__email'))
    today = datetime.today()
    news = Post.objects.filter(datetime__lte=today, datetime__gt=today - timedelta(days=7))
    text_content = f'Новости за эту неделю'
    html_content = render_to_string('celery_weekly_email.html', {'news': news})
    msg = EmailMultiAlternatives(
        subject='Читайте новости за эту неделю',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()