from django.contrib import admin
from django.urls import path, include
from .views import redirector
from django.conf.urls.static import static
from ChatApp import settings
from chat_app import views as chat_views


urlpatterns = [
    path('', redirector),
    path('admin/', admin.site.urls),
    path('chat/', include('chat_app.urls')),
    path('account/', include('account_app.urls')),
    path('accounts/', include('allauth.urls')),
    path('video-call/<slug:room_slug>', chat_views.video_call, name='video_call'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
