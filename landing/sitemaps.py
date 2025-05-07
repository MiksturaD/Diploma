from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Event, Place

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        # Исправляем имена маршрутов в соответствии с urls.py
        return ['index', 'contacts', 'events', 'reviews', 'gourmands', 'places']

    def location(self, item):
        try:
            return reverse(item)
        except Exception as e:
            print(f"Error reversing URL {item}: {e}")
            return "/"

    def lastmod(self, item):
        last_mod_dates = {
            'index': timezone.now(),
            'contacts': timezone.make_aware(datetime(2025, 4, 1)),
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
        # Поля created_at нет, используем дату создания или текущую дату
        return timezone.now()

    def location(self, obj):
        # Указываем маршрут для события (по slug)
        return reverse('event', args=[obj.slug])

class PlaceSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Place.objects.all()

    def lastmod(self, obj):
        # Поля updated_at нет, используем текущую дату
        return timezone.now()

    def location(self, obj):
        # Указываем маршрут для места (по slug)
        return reverse('place', args=[obj.slug])