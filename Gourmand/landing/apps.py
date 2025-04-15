from django.apps import AppConfig

class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Gourmand.landing'

    def ready(self):
        import Gourmand.landing.signals  # Подключаем сигналы
