from django.contrib import admin
from django.urls import path, include
from .views import redirector
from django.conf.urls.static import static
from ChatApp import settings


urlpatterns = [
    path('', redirector),
    path('admin/', admin.site.urls),
    path('chat/', include('chat_app.urls')),
    path('account/', include('account_app.urls')),
    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
