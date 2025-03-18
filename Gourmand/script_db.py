# Запускай через: python manage.py shell
from landing.models import User, Place, Review, NPSResponse, NPSTag
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

# Текущий и прошлый месяц
today = datetime.today()
current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
last_month = current_month - relativedelta(months=1)

# Владелец с ID 7
try:
    owner = User.objects.get(id=7)
    print(f"Owner: {owner.email} (ID: {owner.id}, Role: {owner.role})")
except User.DoesNotExist:
    print("Пользователь с ID 7 не найден! Создаём нового.")
    owner = User.objects.create_user(
        email='owner7@example.com',
        password='12345',
        first_name='Пётр',
        last_name='Владелец',
        role='owner'
    )
    print(f"Создан новый owner: {owner.email} (ID: {owner.id}, Role: {owner.role})")

# Гурман (берём ID 8 или создаём нового)
try:
    gourmand = User.objects.get(id=8)
    print(f"Gourmand: {gourmand.email} (ID: {gourmand.id}, Role: {gourmand.role})")
except User.DoesNotExist:
    print("Гурман с ID 8 не найден! Создаём нового.")
    gourmand = User.objects.create_user(
        email='gourmand8@example.com',
        password='12345',
        first_name='Иван',
        last_name='Гурман',
        role='gourmand'
    )
    print(f"Создан новый gourmand: {gourmand.email} (ID: {gourmand.id}, Role: {gourmand.role})")

# Заведения для владельца
places = [
    Place.objects.get_or_create(
        name="Кафе у Пети",
        owner=owner,
        description="Уютное кафе",
        place_email="cafe@example.com",
        location="ул. Пушкина, 1",
        phone="+79991234567"
    )[0],
    Place.objects.get_or_create(
        name="Бар у Васи",
        owner=owner,
        description="Шумный бар",
        place_email="bar@example.com",
        location="ул. Лермонтова, 2",
        phone="+79997654321"
    )[0],
    Place.objects.get_or_create(
        name="Ресторанчик",
        owner=owner,
        description="Тихий ресторан",
        place_email="rest@example.com",
        location="ул. Гоголя, 3",
        phone="+79999876543"
    )[0],
]

# Теги (создаём, если их нет)
tags = [
    NPSTag.objects.get_or_create(name='kitchen', label='Кухня')[0],
    NPSTag.objects.get_or_create(name='service', label='Обслуживание')[0],
    NPSTag.objects.get_or_create(name='atmosphere', label='Атмосфера')[0],
    NPSTag.objects.get_or_create(name='price', label='Цена')[0],
    NPSTag.objects.get_or_create(name='cleanliness', label='Чистота')[0],
]

# Генерация отзывов и NPS от гурмана
for place in places:
    for _ in range(random.randint(8, 16)):  # 8-16 отзывов на заведение
        # Случайная дата: текущий или прошлый месяц
        if random.choice([True, False]):
            review_date = current_month.replace(day=random.randint(1, 28))
        else:
            review_date = last_month.replace(day=random.randint(1, 28))

        # Отзыв от гурмана (без created_at, используем review_date позже)
        review = Review.objects.create(
            name=f"Отзыв {random.randint(1, 100)}",
            description=f"Это было {'круто' if random.random() > 0.5 else 'не очень'}, еда - {'вкусная' if random.random() > 0.5 else 'так себе'}!",
            place=place,
            gourmand=gourmand,
            gourmand_rating=random.randint(1, 5)
        )
        # Обновляем review_date вручную, обходя auto_now_add
        Review.objects.filter(id=review.id).update(review_date=review_date)

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

# Проверка
print(f"Places for owner {owner.email}: {Place.objects.filter(owner=owner).count()}")
print(f"Reviews by gourmand {gourmand.email}: {Review.objects.filter(gourmand=gourmand).count()}")
print(f"NPS Responses: {NPSResponse.objects.count()}")