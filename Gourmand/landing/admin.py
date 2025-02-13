from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from landing.models import Review, Place, Event, User, GourmandProfile, OwnerProfile, Gourmand

admin.site.register(Place)
admin.site.register(Review)
admin.site.register(GourmandProfile)
admin.site.register(OwnerProfile)
admin.site.register(Event)
admin.site.register(Gourmand)



class UserAdmin(BaseUserAdmin):
  list_display = ("email", "first_name", "last_name", "role", "is_staff")
  search_fields = ("email", "first_name", "last_name")
  ordering = ("email",)
  fieldsets = (
    (None, {"fields": ("email", "password")}),
    ("Персональная информация", {"fields": ("first_name", "last_name", "role")}),
    ("Разрешения", {"fields": ("is_active", "is_staff", "is_superuser")}),
  )
  add_fieldsets = (
    (None, {
      "classes": ("wide",),
      "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
    }),
  )


admin.site.register(User, UserAdmin)
