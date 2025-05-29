# Этот файл содержит сигналы Django, которые автоматически выполняются при определённых событиях с моделями.
# Здесь мы обрабатываем события создания и сохранения пользователя (User), чтобы управлять связанными профилями.

from django.db.models.signals import post_save  # Импортируем сигнал post_save, который срабатывает после сохранения объекта.
from django.dispatch import receiver  # Импортируем декоратор receiver для привязки функций к сигналам.
from .models import User, GourmandProfile, OwnerProfile  # Импортируем модели, с которыми будем работать.


# Декоратор receiver связывает функцию с сигналом post_save для модели User.
# Срабатывает после создания нового пользователя.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Создаёт профиль пользователя (GourmandProfile или OwnerProfile) при создании нового пользователя.

    Args:
        sender: Класс модели, отправивший сигнал (в данном случае User).
        instance: Экземпляр модели User, который был сохранён.
        created: Булево значение, True, если пользователь только что создан.
        **kwargs: Дополнительные аргументы, переданные сигналу.
    """
    if created:  # Проверяем, что пользователь только что создан (а не обновлён).
        if instance.role == 'gourmand':  # Если роль пользователя — гурман.
            GourmandProfile.objects.create(user=instance)  # Создаём профиль гурмана, связанный с этим пользователем.
        elif instance.role == 'owner':  # Если роль пользователя — владелец заведения.
            OwnerProfile.objects.create(user=instance)  # Создаём профиль владельца, связанный с этим пользователем.


# Декоратор receiver связывает функцию с сигналом post_save для модели User.
# Срабатывает после каждого сохранения пользователя (как при создании, так и при обновлении).
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сохраняет профиль пользователя (GourmandProfile или OwnerProfile) при обновлении пользователя.

    Args:
        sender: Класс модели, отправивший сигнал (в данном случае User).
        instance: Экземпляр модели User, который был сохранён.
        **kwargs: Дополнительные аргументы, переданные сигналу.
    """
    # Проверяем роль пользователя и наличие связанного профиля.
    if instance.role == 'gourmand' and hasattr(instance, 'gourmandprofile'):
        # Если пользователь — гурман и у него есть профиль гурмана (gourmandprofile),
        # сохраняем профиль, чтобы обновить связанные данные (например, рейтинг).
        instance.gourmandprofile.save()
    elif instance.role == 'owner' and hasattr(instance, 'ownerprofile'):
        # Если пользователь — владелец и у него есть профиль владельца (ownerprofile),
        # сохраняем профиль, чтобы обновить связанные данные.
        instance.ownerprofile.save()