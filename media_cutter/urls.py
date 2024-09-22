from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import index


urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("app/", include("core.urls")),
    path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)