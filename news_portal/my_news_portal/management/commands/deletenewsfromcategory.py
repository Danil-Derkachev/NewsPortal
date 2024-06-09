from django.core.management.base import BaseCommand, CommandError
from my_news_portal.models import Post, Category


class Command(BaseCommand):
    help = 'Подсказка вашей команды'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    requires_migrations_checks = True  # напоминать ли о миграциях. Если true — то будет напоминание о том, что не сделаны все миграции (если такие есть)

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        try:
            Category.objects.get(name=options['category'])

        except Exception:
                self.stdout.write(self.style.ERROR(f'Категории {options["category"]} не существует.'))

        else:
            answer = input(f'Вы правда хотите удалить все новости в категории {options["category"]}? yes/no: ')
            if answer == 'yes':  # в случае подтверждения действительно удаляем все новости из категории
                Post.objects.filter(type='NE', categories__name=options['category']).delete()
                self.stdout.write(self.style.SUCCESS(f'Все новости в категории {options["category"]} удалены.'))
                return

            self.stdout.write(
                self.style.ERROR('Отменено'))
