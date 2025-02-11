from django.apps import AppConfig


class GourmandConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'

class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'

    def ready(self):
        import landing.signals  # Подключаем сигналы
