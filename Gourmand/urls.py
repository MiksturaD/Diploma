"""
URL configuration for The_Project_Gourmand project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Импортируем функцию static для обслуживания медиафайлов в режиме отладки.
from django.conf.urls.static import static
# Импортируем модуль admin для подключения админ-панели Django.
from django.contrib import admin
# Импортируем функции path и include для определения маршрутов и включения других URL-конфигураций.
from django.urls import path, include
# Импортируем представления для авторизации (например, сброса пароля) из Django.
from django.contrib.auth import views as auth_views
# Импортируем настройки проекта из settings.py.
from django.conf import settings
# Импортируем представления для генерации sitemap.
from django.contrib.sitemaps import views as sitemap_views
# Импортируем классы sitemap из приложения landing для генерации карты сайта.
from landing.sitemaps import StaticViewSitemap, EventSitemap, PlaceSitemap

# Создаём словарь sitemaps, который связывает имена с классами sitemap.
# Это нужно для генерации карты сайта (sitemap.xml).
sitemaps = {
    'static': StaticViewSitemap,  # Sitemap для статических страниц (например, главная, контакты).
    'events': EventSitemap,  # Sitemap для динамических страниц событий (Event).
    'places': PlaceSitemap,  # Sitemap для динамических страниц мест (Place).
}

# Список маршрутов (URL patterns), которые определяют, как запросы обрабатываются.
urlpatterns = [
    # Маршрут для админ-панели Django, доступной по адресу /admin/.
    path('admin/', admin.site.urls),

    # Включаем все маршруты из приложения landing (landing/urls.py).
    # Пустой путь '' означает, что маршруты начинаются с корня сайта.
    path('', include('landing.urls')),

    # Маршрут для карты сайта (sitemap.xml).
    # Используем представление sitemap_views.sitemap, передавая словарь sitemaps.
    path('sitemap.xml', sitemap_views.sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Маршрут для страницы сброса пароля.
    # Используем встроенное представление PasswordResetView для отправки письма с инструкциями по сбросу.
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html',  # Шаблон формы сброса пароля.
        email_template_name='auth/password_reset_email.html',  # Шаблон письма для сброса.
        subject_template_name='auth/password_reset_subject.txt',  # Шаблон темы письма.
        from_email='aagubanoff@yandex.ru',  # Email-адрес отправителя.
    ), name='password_reset'),

    # Маршрут для страницы, показывающей, что письмо для сброса пароля отправлено.
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'  # Шаблон страницы подтверждения отправки.
    ), name='password_reset_done'),

    # Маршрут для страницы подтверждения нового пароля.
    # Принимает uidb64 (ID пользователя в base64) и token для проверки.
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'  # Шаблон формы для ввода нового пароля.
    ), name='password_reset_confirm'),

    # Маршрут для страницы, показывающей, что сброс пароля успешно завершён.
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'  # Шаблон страницы успешного завершения.
    ), name='password_reset_complete'),
]

# Условный блок: если включён режим отладки (DEBUG=True),
# добавляем маршруты для обслуживания медиафайлов (например, изображений).
if settings.DEBUG:
    # static добавляет маршрут для доступа к файлам по MEDIA_URL,
    # используя папку MEDIA_ROOT для хранения.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)