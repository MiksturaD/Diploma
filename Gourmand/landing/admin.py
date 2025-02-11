from django.contrib import admin

from landing.models import Review, Place, Event, User, GourmandProfile, OwnerProfile

admin.site.register(Place)
admin.site.register(Review)
admin.site.register(GourmandProfile)
admin.site.register(OwnerProfile)
admin.site.register(Event)
admin.site.register(User)
