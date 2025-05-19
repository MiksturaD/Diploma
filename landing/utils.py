from datetime import timedelta
from django.utils import timezone
from .models import Review
from django.conf import settings
from dotenv import load_dotenv
import os
import logging

from openai import OpenAI

# Логгер для ошибок
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Создаём клиент OpenAI для OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
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
        nps_tags = ", ".join(tag.label for tag in getattr(nps, "tags", []).all()) if nps and hasattr(nps, "tags") else "нет тегов"

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
    logger.info(f"CHATGPT_UTIL: Analyzing reviews for '{place_name}'")
    if reviews_data == "Нет отзывов за выбранный период.":
        logger.info(f"CHATGPT_UTIL: No reviews for '{place_name}'. Returning message.")
        return reviews_data

    if len(reviews_data) > 3500: # Ограничение по длине
        reviews_data = reviews_data[:3500] + "... (обрезано)"
        logger.debug(f"CHATGPT_UTIL: Review data for '{place_name}' was truncated.")

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
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "Ты аналитик, который помогает владельцам ресторанов понимать отзывы клиентов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            extra_headers={ # Попробуйте закомментировать, если есть сомнения
                "HTTP-Referer": "http://212.192.217.30/",
                "X-Title": "Gourmand",
            },
            extra_body={} # Обычно не требуется
        )
        summary_content = response.choices[0].message.content.strip()
        logger.info(f"CHATGPT_UTIL: Successfully received summary for '{place_name}': '{summary_content[:100]}...'")
        return summary_content
    except Exception as e:
        logger.exception(f"CHATGPT_UTIL: Error analyzing reviews for '{place_name}' via OpenRouter: {e}")
        return "Не удалось получить сводку по отзывам. Попробуйте позже."