from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from news_portal import settings
from .models import *


@receiver(m2m_changed, sender=PostCategory)
def notify_subscribed_users(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        if instance.type == 'NE':
            instance_categories = instance.categories.values_list('name', flat=True)
            subscribers_emails = set(Subscriber.objects.filter(category__name__in=instance_categories).values_list('user__email', flat=True))
            text_content = f'Прочитайте новую новость {instance.title}'
            html_content = render_to_string('email.html', {'news': instance, 'id': instance.id})
            msg = EmailMultiAlternatives(
                subject=instance.title,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=subscribers_emails
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
