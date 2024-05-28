from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

#from news_portal.settings import DEFAULT_FROM_EMAIL
from .models import *

@receiver(m2m_changed, sender=PostCategory)
def notify_subscribed_users(sender, instance, created, **kwargs):
    if kwargs['action'] == 'post_add':
        instance_categories_list = instance.categories.values_list('name', flat=True)
        subscribers = set(Subscriber.objects.filter(category__in=instance_categories_list).values_list('user__email', flat=True))
        text_content = f'Прочитайте новую новость {instance.title}'
        html_content = render_to_string('email.html', {'news': instance})
        msg = EmailMultiAlternatives(
            subject=instance.title,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
