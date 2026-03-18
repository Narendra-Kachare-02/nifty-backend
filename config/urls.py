
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework_simplejwt.views import TokenObtainPairView
from dashboard_backend.users.views import token_refresh
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # API base url
    path("api/", include("config.api_router")),
     # API schema
    path("api/", include("dashboard_backend.users.urls", namespace="users")),
    path("api/nifty/", include("dashboard_backend.nifty.urls", namespace="nifty")),

    # Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('admin/', admin.site.urls),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', token_refresh, name='token_refresh'),

    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += path('__debug__/',include(debug_toolbar.urls)),

    urlpatterns += staticfiles_urlpatterns()
    