from django.apps import AppConfig


class AppointmentConfig(AppConfig):
    name = 'appointment'

    # нам надо переопределить метод ready, чтобы при готовности нашего приложения импортировался модуль со всеми функциями обработчиками
    def ready(self):
        import appointment.signals

    # from .tasks import send_mails
    # from .scheduler import appointment_schedular
    # print('started')
    #
    # appointment_schedular.add_job(
    #     id='mail send',
    #     func=send_mails,
    #     trigger='interval',
    #     seconds=10,
    # )
    # appointment_schedular.start()

