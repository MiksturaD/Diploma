# your_app/utils.py
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Review
import openai
from django.conf import settings

def get_reviews_for_last_month(place, days=30):
  """
  Собирает отзывы за указанный период (по умолчанию 30 дней) для конкретного заведения.
  """
  now = timezone.now()
  start_date = now - timedelta(days=days)
  reviews = Review.objects.filter(
    place=place,
    review_date__gte=start_date,
    review_date__lte=now
  )
  return reviews


def prepare_reviews_data(reviews):
  """
  Подготавливает данные отзывов для отправки в ChatGPT.
  Включает текст отзыва, NPS-оценку, теги и рейтинги.
  """
  if not reviews.exists():
    return "Нет отзывов за выбранный период."

  reviews_data = []
  for review in reviews:
    nps = review.nps if hasattr(review, 'nps') else None
    nps_score = nps.score if nps else "не указана"
    nps_tags = ", ".join(tag.label for tag in nps.tags.all()) if nps and nps.tags.exists() else "нет тегов"

    review_info = (
      f"Отзыв: {review.description}\n"
      f"NPS-оценка: {nps_score}\n"
      f"Теги: {nps_tags}\n"
      f"Положительный рейтинг: {review.positive_rating}, Отрицательный рейтинг: {review.negative_rating}\n"
    )
    reviews_data.append(review_info)

  return "\n---\n".join(reviews_data)


def get_tag_stats(reviews):
  """
  Собирает статистику по тегам из NPS-ответов.
  """
  tag_counts = {}
  for review in reviews:
    if hasattr(review, 'nps'):
      for tag in review.nps.tags.all():
        tag_counts[tag.label] = tag_counts.get(tag.label, 0) + 1
  return tag_counts

openai.api_key = settings.OPENAI_API_KEY

def analyze_reviews_with_chatgpt(reviews_data, place_name):
    """
    Отправляет данные отзывов в ChatGPT и возвращает сводку.
    """
    if reviews_data == "Нет отзывов за выбранный период.":
        return reviews_data

    prompt = (
        f"Проанализируй отзывы о заведении '{place_name}' за выбранный период. "
        "Каждый отзыв включает текст, NPS-оценку (от 1 до 10), теги (например, 'Кухня', 'Обслуживание') и рейтинги (положительный и отрицательный). "
        "Составь краткую сводку в следующем формате:\n"
        "- Средняя NPS-оценка: [укажи среднюю оценку]\n"
        "- Положительные моменты: [перечисли, что хвалят, и укажи, какие теги чаще упоминаются]\n"
        "- Отрицательные моменты: [перечисли, на что жалуются, и укажи, какие теги связаны с жалобами]\n"
        "- Рекомендации: [дай 1-2 рекомендации для улучшения]\n\n"
        "Вот данные:\n\n{reviews_data}\n\n"
        "Ответ должен быть на русском языке и не превышать 200 слов."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты аналитик, который помогает владельцам ресторанов понимать отзывы клиентов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        summary = response.choices[0].message['content'].strip()
        return summary
    except Exception as e:
        return f"Ошибка при анализе отзывов: {str(e)}"