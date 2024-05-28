from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from news_portal.settings import DEFAULT_FROM_EMAIL
from .models import *

@receiver(post_save, sender=Post)
def notify_subscribed_users(sender, instance, created, **kwargs):
    if created:
        instance_categories_list = instance.objects.values_list('categories__name')
        subscribers = Subscriber.objects.filter(category__in=instance_categories_list).values_list('user__email')
        text_content = f'Прочитайте новую новость {instance.title}'
        html_content = render_to_string('email.html', {'news': instance})
        msg = EmailMultiAlternatives(
            subject=instance.title,
            body=text_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=subscribers
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
