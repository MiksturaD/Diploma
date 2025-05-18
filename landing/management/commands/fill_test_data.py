from django.core.management.base import BaseCommand
from landing.models import User, Place, Review, NPSResponse, NPSTag, ReviewVote
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми отзывами о заведениях'

    def handle(self, *args, **kwargs):
        # Текущий и прошлый месяц
        today = datetime.today()
        current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = current_month - relativedelta(months=1)

        # Получаем гурманов (ID 3-6 и 8-9)
        gourmand_ids = [3, 4, 5, 6, 8, 9]
        gourmands = []
        for gid in gourmand_ids:
            try:
                gourmand = User.objects.get(id=gid, role='gourmand')
                gourmands.append(gourmand)
                self.stdout.write(
                    self.style.SUCCESS(f"Гурман найден: {gourmand.email} (ID: {gourmand.id}, Role: {gourmand.role})"))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Гурман с ID {gid} не найден! Пропускаем."))

        if not gourmands:
            self.stdout.write(self.style.ERROR("Ни одного гурмана не найдено! Завершаем выполнение."))
            return

        # Получаем заведения (ID 5-14)
        place_ids = list(range(5, 15))  # ID от 5 до 14
        places = []
        for pid in place_ids:
            try:
                place = Place.objects.get(id=pid)
                places.append(place)
                self.stdout.write(self.style.SUCCESS(f"Заведение найдено: {place.name} (ID: {place.id})"))
            except Place.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Заведение с ID {pid} не найдено! Пропускаем."))

        if not places:
            self.stdout.write(self.style.ERROR("Ни одного заведения не найдено! Завершаем выполнение."))
            return

        # Теги (создаём, если их нет)
        tags = [
            NPSTag.objects.get_or_create(name='kitchen', label='Кухня')[0],
            NPSTag.objects.get_or_create(name='service', label='Обслуживание')[0],
            NPSTag.objects.get_or_create(name='atmosphere', label='Атмосфера')[0],
            NPSTag.objects.get_or_create(name='price', label='Цена')[0],
            NPSTag.objects.get_or_create(name='cleanliness', label='Чистота')[0],
        ]

        # Варианты для генерации текста отзывов
        food_comments = [
            "еда была невероятно вкусной","издевательство над едой", "блюда оставили желать лучшего", "вкусная еда, но порции маленькие",
            "кухня на высоте", "еда была пересоленной","никогда в жизни не ел такой пакости как тут!", "всё свежее и аппетитное", "неплохая кухня, но ожидал большего"
        ]
        service_comments = [
            "обслуживание на высшем уровне", "официанты были медленными","персонал дал мне денег, чтобы я ел", "персонал очень вежливый",
            "сервис оставил неприятное впечатление", "официанты забывали заказы", "быстрое и качественное обслуживание"
        ]
        atmosphere_comments = [
            "атмосфера уютная и тёплая", "слишком шумно","рок-н-ролл детка!", "интерьер потрясающий", "чувствуется какая-то холодность",
            "идеальное место для ужина", "атмосфера не располагает к отдыху"
        ]
        price_comments = [
            "цены вполне адекватные", "слишком дорого для такого качества", "хорошее соотношение цены и качества",
            "цены кусаются", "ожидал меньший счёт","да я бесплатно ем тут всегда"
        ]

        # Счётчик для уникальных названий отзывов
        review_counter = 1

        # Генерация отзывов
        for place in places:
            num_reviews = random.randint(2, 10)  # Случайное количество отзывов (2-10)
            self.stdout.write(
                self.style.SUCCESS(f"Генерируем {num_reviews} отзывов для заведения {place.name} (ID: {place.id})"))

            for _ in range(num_reviews):
                # Случайный гурман
                gourmand = random.choice(gourmands)

                # Случайная дата: текущий или прошлый месяц
                if random.choice([True, False]):
                    review_date = current_month.replace(day=random.randint(1, 28))
                else:
                    review_date = last_month.replace(day=random.randint(1, 28))

                # Генерируем текст отзыва
                description = f"{random.choice(food_comments)}, {random.choice(service_comments)}, {random.choice(atmosphere_comments)}, {random.choice(price_comments)}."
                gourmand_rating = random.randint(1, 5)

                # Создаём отзыв
                review = Review.objects.create(
                    name=f"Отзыв {review_counter}",
                    description=description,
                    place=place,
                    gourmand=gourmand,
                    gourmand_rating=gourmand_rating,
                )
                # Обновляем review_date вручную, обходя auto_now_add
                Review.objects.filter(id=review.id).update(review_date=review_date)

                # Генерируем голоса (ReviewVote)
                num_votes = random.randint(0, len(gourmands))  # Случайное количество голосов (0 до числа гурманов)
                voters = random.sample(gourmands, num_votes)  # Случайные гурманы, которые проголосуют
                for voter in voters:
                    # Пропускаем, если это сам автор отзыва
                    if voter == gourmand:
                        continue
                    # Случайный тип голоса: positive или negative
                    vote_type = random.choice(['positive', 'negative'])
                    ReviewVote.objects.create(
                        review=review,
                        user=voter,
                        vote_type=vote_type
                    )

                # Обновляем счётчики positive_rating и negative_rating
                review.positive_rating = review.votes.filter(vote_type='positive').count()
                review.negative_rating = review.votes.filter(vote_type='negative').count()
                review.save(update_fields=['positive_rating', 'negative_rating'])

                # NPS от гурмана
                nps_score = random.randint(1, 10)
                nps = NPSResponse.objects.create(
                    review=review,
                    score=nps_score,
                    created_at=review_date
                )
                # Добавляем случайные теги (1-3 штуки)
                selected_tags = random.sample(tags, random.randint(1, 3))
                nps.tags.set(selected_tags)

                # Увеличиваем счётчик
                review_counter += 1

        # Проверка
        self.stdout.write(self.style.SUCCESS(f"Всего создано отзывов: {Review.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Всего создано NPS-ответов: {NPSResponse.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Всего создано голосов: {ReviewVote.objects.count()}"))
        for gourmand in gourmands:
            self.stdout.write(self.style.SUCCESS(
                f"Отзывы от гурмана {gourmand.email}: {Review.objects.filter(gourmand=gourmand).count()}"))
            self.stdout.write(self.style.SUCCESS(
                f"Голоса от гурмана {gourmand.email}: {ReviewVote.objects.filter(user=gourmand).count()}"))
        for place in places:
            self.stdout.write(
                self.style.SUCCESS(f"Отзывы о заведении {place.name}: {Review.objects.filter(place=place).count()}"))