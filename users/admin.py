from django.contrib import admin

# Register your models here.
from events.models import Category, Event, RSVP
admin.site.register(Event)
admin.site.register(RSVP)