from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from events.views import home, details, dashboard, create_event, update_participant

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('event/<int:id>/', details, name='details'),
    path('event/<int:event_id>/<int:participant_id>/', update_participant, name='update_participant'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create-event/', create_event, name='create_event'),
    # path('home/', home)
]+ debug_toolbar_urls()
