from django.urls import path

from .views import latest, latestOptionChain, niftySeries


app_name = "nifty"

urlpatterns = [
    path("latest/", latest, name="latest"),
    path("option-chain/latest/", latestOptionChain, name="option-chain-latest"),
    path("series/", niftySeries, name="series"),
]

