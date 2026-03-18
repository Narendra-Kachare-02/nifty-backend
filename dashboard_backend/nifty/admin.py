from django.contrib import admin
from .models import NiftySnapshot, OptionChainSnapshot, NiftyChartSnapshot

admin.site.register(NiftySnapshot)
admin.site.register(OptionChainSnapshot)
admin.site.register(NiftyChartSnapshot)