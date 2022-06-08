from django.contrib import admin
from .models import WeatherHistory, EnergyBill, WeatherObservations, SunData, EnergyUse, SolarGeneration

# Register your models here.
admin.site.register(WeatherObservations)
admin.site.register(SunData)
admin.site.register(WeatherHistory)
admin.site.register(EnergyBill)
admin.site.register(EnergyUse)
admin.site.register(SolarGeneration)