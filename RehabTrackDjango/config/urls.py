"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Django's built-in admin (for debugging only, as requested)
    path('django-admin/', admin.site.urls),
    
    # Custom Admin Panel UI endpoints
    path('admin-panel/', include('core.urls_admin')),
    
    # Core API endpoints
    path('api/', include('core.urls')),
    
    # Client Portal UI endpoints
    path('portal/', include('core.urls_portal')),
    
    # Mobile App REST APIs
    path('api/v1/', include('core.api_urls')),
    
    # Root URL redirect to Portal Login
    path('', RedirectView.as_view(url='/portal/login/', permanent=False), name='index'),
]
