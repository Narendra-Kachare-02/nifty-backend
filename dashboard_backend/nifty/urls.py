from django.urls import path

from .views import latest


app_name = "nifty"

urlpatterns = [
    path("latest/", latest, name="latest"),
]

