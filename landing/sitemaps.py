# Импорт модуля datetime для работы с датами в явном виде (например, для примера даты).
from datetime import datetime

# Импорт базового класса Sitemap из Django для создания карты сайта.
from django.contrib.sitemaps import Sitemap

# Импорт функции reverse для преобразования имен маршрутов в URL.
from django.urls import reverse

# Импорт утилиты timezone из Django для работы с временными зонами и текущей датой.
from django.utils import timezone

# Импорт моделей Event и Place из текущего приложения для динамической генерации URL.
from .models import Event, Place


# Класс StaticViewSitemap наследуется от Sitemap и отвечает за статические страницы сайта.
# Используется для страниц, которые не зависят от данных из базы (например, главная, контакты).
class StaticViewSitemap(Sitemap):
    # Устанавливаем приоритет страницы (0.0–1.0), 0.5 — средний приоритет для статических страниц.
    priority = 0.5

    # Указываем частоту изменения страниц, 'daily' — ежедневно, чтобы поисковики чаще проверяли.
    changefreq = 'daily'

    # Метод items возвращает список имен маршрутов, которые нужно включить в sitemap.
    # Эти имена должны соответствовать name в urls.py.
    def items(self):
        # Исправляем имена маршрутов в соответствии с urls.py, чтобы избежать ошибок NoReverseMatch.
        return ['index', 'contacts', 'events', 'reviews', 'gourmands', 'places']

    # Метод location генерирует URL для каждого элемента из items.
    # Преобразует имя маршрута в полный URL с помощью reverse.
    def location(self, item):
        try:
            # Пытаемся преобразовать имя маршрута в URL, если маршрут существует.
            return reverse(item)
        except Exception as e:
            # Если маршрут не найден, выводим ошибку в консоль для отладки и возвращаем корневой URL.
            print(f"Error reversing URL {item}: {e}")
            return "/"

    # Метод lastmod определяет дату последнего изменения страницы.
    # Возвращает дату в формате, подходящем для sitemap.
    def lastmod(self, item):
        # Создаём словарь с датами последнего изменения для каждой страницы.
        # Если точной даты нет, используем текущую дату через timezone.now().
        last_mod_dates = {
            'index': timezone.now(),  # Главная страница, обновляется сейчас как пример.
            'contacts': timezone.make_aware(datetime(2025, 4, 1)),  # Пример даты для контактов.
            'events': timezone.now(),  # Список событий, обновляется сейчас.
            'reviews': timezone.now(),  # Страница отзывов, обновляется сейчас.
            'gourmands': timezone.now(),  # Страница гурманов, обновляется сейчас.
            'places': timezone.now(),  # Список мест, обновляется сейчас.
        }
        # Возвращаем дату из словаря для текущего item, если её нет — текущую дату.
        return last_mod_dates.get(item, timezone.now())


# Класс EventSitemap наследуется от Sitemap и отвечает за динамические страницы событий.
# Генерирует URL для каждого объекта Event из базы данных.
class EventSitemap(Sitemap):
    # Устанавливаем приоритет страниц событий (0.7 — выше среднего, так как события важны).
    priority = 0.7

    # Указываем частоту изменения, 'weekly' — раз в неделю, так как события обновляются нечасто.
    changefreq = 'weekly'

    # Метод items возвращает все объекты Event из базы для включения в sitemap.
    def items(self):
        return Event.objects.all()

    # Метод lastmod определяет дату последнего изменения объекта.
    # Поскольку поля created_at нет, возвращаем текущую дату как запасной вариант.
    def lastmod(self, obj):
        # Поля created_at нет, используем текущую дату как временное решение.
        # (Рекомендуется добавить created_at в модель Event для точности.)
        return timezone.now()

    # Метод location генерирует URL для конкретного объекта Event.
    # Использует маршрут 'event' с аргументом slug.
    def location(self, obj):
        # Указываем маршрут для события (по slug), соответствует urls.py.
        return reverse('event', args=[obj.slug])


# Класс PlaceSitemap наследуется от Sitemap и отвечает за динамические страницы мест.
# Генерирует URL для каждого объекта Place из базы данных.
class PlaceSitemap(Sitemap):
    # Устанавливаем приоритет страниц мест (0.6 — средний, чуть ниже событий).
    priority = 0.6

    # Указываем частоту изменения, 'weekly' — раз в неделю, так как места обновляются редко.
    changefreq = 'weekly'

    # Метод items возвращает все объекты Place из базы для включения в sitemap.
    def items(self):
        return Place.objects.all()

    # Метод lastmod определяет дату последнего изменения объекта.
    # Поскольку поля updated_at нет, возвращаем текущую дату как запасной вариант.
    def lastmod(self, obj):
        # Поля updated_at нет, используем текущую дату как временное решение.
        # (Рекомендуется добавить updated_at в модель Place для точности.)
        return timezone.now()

    # Метод location генерирует URL для конкретного объекта Place.
    # Использует маршрут 'place' с аргументом slug.
    def location(self, obj):
        # Указываем маршрут для места (по slug), соответствует urls.py.
        return reverse('place', args=[obj.slug])