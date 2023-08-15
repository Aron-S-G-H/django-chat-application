from django.contrib import admin
from django.urls import path, include
from .views import redirector


urlpatterns = [
    path('', redirector),
    path('admin/', admin.site.urls),
    path('chat/', include('chat_app.urls')),
    path('account/', include('account_app.urls')),
]
