from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login'), name='home'),
    path('auth/', include('accounts.urls')),
    path('dashboard/', include('core.urls')),
    path('projects/', include('projects.urls')),
    path('payments/', include('payments.urls')),
    path('communication/', include('communication.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
