from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter



# from property_backend.users.api.views import  UserDetailView, AddressDetailView
# router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router = SimpleRouter() 

# router.register("users", UserViewSet)
# router.register("userdetails", UserDetailView, basename="user_details")
# router.register("address", AddressDetailView, basename="addresses")



app_name = "api"
urlpatterns = router.urls + [
    # path('rera/', include('property_backend.rera.urls')),
]
