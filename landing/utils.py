from datetime import timedelta
from django.utils import timezone
from .models import Review
from django.conf import settings
from dotenv import load_dotenv
import os

from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

# Создаём клиент OpenAI для OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def get_reviews_for_last_month(place, days=30):
    now = timezone.now()
    start_date = now - timedelta(days=days)
    return Review.objects.filter(place=place, review_date__range=(start_date, now))

def prepare_reviews_data(reviews):
    if not reviews.exists():
        return "Нет отзывов за выбранный период."

    reviews_data = []
    for review in reviews:
        nps = getattr(review, "nps", None)
        nps_score = getattr(nps, "score", "не указана")
        nps_tags = ", ".join(tag.label for tag in getattr(nps, "tags", [])) if nps and hasattr(nps, "tags") else "нет тегов"

        reviews_data.append(
            f"Отзыв: {review.description}\n"
            f"NPS-оценка: {nps_score}\n"
            f"Теги: {nps_tags}\n"
            f"Положительный рейтинг: {review.positive_rating}, Отрицательный рейтинг: {review.negative_rating}"
        )
    return "\n---\n".join(reviews_data)

def get_tag_stats(reviews):
    tag_counts = {}
    for review in reviews:
        nps = getattr(review, "nps", None)
        if nps and hasattr(nps, "tags"):
            for tag in nps.tags.all():
                tag_counts[tag.label] = tag_counts.get(tag.label, 0) + 1
    return tag_counts

def analyze_reviews_with_chatgpt(reviews_data, place_name):
    """
    Отправляет данные отзывов в модель через OpenRouter и возвращает сводку.
    """
    if reviews_data == "Нет отзывов за выбранный период.":
        return reviews_data

    prompt = (
        f"Проанализируй отзывы о заведении '{place_name}' за выбранный период. "
        "Каждый отзыв включает текст, NPS-оценку (от 1 до 10), теги (например, 'Кухня', 'Обслуживание') и рейтинги (положительный и отрицательный). "
        "Составь краткую сводку в следующем формате:\n"
        "- Средняя NPS-оценка: [укажи среднюю оценку]\n"
        "- Положительные моменты: [что хвалят, какие теги чаще]\n"
        "- Отрицательные моменты: [на что жалуются, какие теги связаны]\n"
        "- Рекомендации: [1-2 рекомендации для улучшения]\n\n"
        "Вот данные:\n\n{reviews_data}\n\n"
        "Ответ должен быть на русском языке и не превышать 200 слов."
    )

    try:
        response = client.chat.completions.create(
            model="microsoft/mai-ds-r1:free",  # Выбранная модель
            messages=[
                {"role": "system", "content": "Ты аналитик, который помогает владельцам ресторанов понимать отзывы клиентов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "http://http://212.192.217.30/",
                "X-Title": "Gourmand",
            },
            extra_body={}
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка при анализе через OpenRouter: {str(e)}"
