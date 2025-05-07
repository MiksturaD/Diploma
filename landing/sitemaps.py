from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone  # Используем Django-версию timezone
from .models import Event, Place  # Убрали дубликат Event и User

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'contact', 'events', 'reviews', 'gourmands', 'places']  # Список статических URL

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Можно задать разные даты или проверять обновления
        last_mod_dates = {
            'home': timezone.now(),
            'contact': timezone.make_aware(datetime(2025, 4, 1)),  # Пример даты
            'events': timezone.now(),
            'reviews': timezone.now(),
            'gourmands': timezone.now(),
            'places': timezone.now(),
        }
        return last_mod_dates.get(item, timezone.now())

class EventSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Event.objects.all()

    def lastmod(self, obj):
        return obj.created_at  # Убедись, что поле created_at существует

class PlaceSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Place.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Убедись, что поле updated_at существует