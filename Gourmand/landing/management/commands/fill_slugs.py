from django.core.management.base import BaseCommand
from landing.models import User, Place, Review, Event
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Заполняет поле slug для существующих записей'

    def handle(self, *args, **kwargs):
        # User
        users = User.objects.all()
        for user in users:
            if not user.slug:
                base_slug = user.first_name + "-" + user.last_name if user.first_name and user.last_name else user.email.split('@')[0]
                user.slug = slugify(base_slug)
                original_slug = user.slug
                counter = 1
                while User.objects.filter(slug=user.slug).exclude(id=user.id).exists():
                    user.slug = f"{original_slug}-{counter}"
                    counter += 1
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Обновлён slug для User {user.email}: {user.slug}'))

        # Place
        places = Place.objects.all()
        for place in places:
            if not place.slug:
                place.slug = slugify(place.name)
                original_slug = place.slug
                counter = 1
                while Place.objects.filter(slug=place.slug).exclude(id=place.id).exists():
                    place.slug = f"{original_slug}-{counter}"
                    counter += 1
                place.save()
                self.stdout.write(self.style.SUCCESS(f'Обновлён slug для Place {place.name}: {place.slug}'))

        # Review
        reviews = Review.objects.all()
        for review in reviews:
            if not review.slug:
                base_slug = f"{review.name}-{review.id}"
                review.slug = slugify(base_slug)
                original_slug = review.slug
                counter = 1
                while Review.objects.filter(slug=review.slug).exclude(id=review.id).exists():
                    review.slug = f"{original_slug}-{counter}"
                    counter += 1
                review.save()
                self.stdout.write(self.style.SUCCESS(f'Обновлён slug для Review {review.name}: {review.slug}'))

        # Event
        events = Event.objects.all()
        for event in events:
            if not event.slug:
                event.slug = slugify(event.name)
                original_slug = event.slug
                counter = 1
                while Event.objects.filter(slug=event.slug).exclude(id=event.id).exists():
                    event.slug = f"{original_slug}-{counter}"
                    counter += 1
                event.save()
                self.stdout.write(self.style.SUCCESS(f'Обновлён slug для Event {event.name}: {event.slug}'))

