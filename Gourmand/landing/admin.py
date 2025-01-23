from django.contrib import admin

from landing.models import Review, Place, Gourmand, Event, User

admin.site.register(Place)
admin.site.register(Review)
admin.site.register(Gourmand)
admin.site.register(Event)
admin.site.register(User)
