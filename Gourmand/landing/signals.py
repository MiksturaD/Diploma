from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, GourmandProfile, OwnerProfile

# 📌 Сигнал будет работать после сохранения объекта User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'gourmand':
            GourmandProfile.objects.create(user=instance)
        elif instance.role == 'owner':
            OwnerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'gourmand' and hasattr(instance, 'gourmandprofile'):
        instance.gourmandprofile.save()
    elif instance.role == 'owner' and hasattr(instance, 'ownerprofile'):
        instance.ownerprofile.save()
