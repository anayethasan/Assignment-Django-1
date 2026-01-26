from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from events.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', home),
    path('home/', home)
]+ debug_toolbar_urls()
