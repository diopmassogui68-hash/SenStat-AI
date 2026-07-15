from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Frontend
    path('', TemplateView.as_view(template_name='chatbot/index.html'), name='home'),
    
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('apps.api.urls')),
    
    # Swagger documentation (Bonus intégré pour la présentation propre de l'API)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
