from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events.views import home, details, dashboard, create_event, quick_rsvp, confirm_rsvp
from core.views import no_permission

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('event/<int:id>/', details, name='details'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create-event/', create_event, name='create_event'),
    path('rsvp/<int:event_id>/', quick_rsvp, name='quick-rsvp'),
    path('rsvp/confirm/<uuid:token>/', confirm_rsvp, name='confirm-rsvp'),
    path('no-permission/', no_permission, name='no-permission'),
    path('user/', include('users.urls')),
]+ debug_toolbar_urls()


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)