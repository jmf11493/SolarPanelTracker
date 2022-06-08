from django.db import models
import uuid

# Create your models here.
class WeatherObservations(models.Model):
    id = models.TextField(primary_key=True)
    date = models.DateField()
    time = models.TimeField() # the "corrected" time 
    observed_time = models.TimeField()
    temperature = models.IntegerField() # degrees F
    dew_point = models.IntegerField() # degrees F
    humidity = models.IntegerField() # percentage
    wind = models.TextField()
    wind_speed = models.IntegerField() # mph
    wind_gust = models.IntegerField() # mph
    pressure = models.FloatField() # inches
    precipitation = models.FloatField() # inches
    condition = models.TextField()

class SunData(models.Model):
    date = models.DateField(primary_key=True)
    hours_sunlight = models.IntegerField() # will be in minutes
    sun_rise = models.TimeField()
    sun_set = models.TimeField()

class WeatherHistory(models.Model):
    id = models.TextField(primary_key=True)
    date = models.DateField()
    type = models.TextField()
    actual = models.FloatField(null=True)
    historic_avg = models.FloatField(null=True)
    historic_record = models.FloatField(null=True)

class EnergyBill(models.Model):
    billing_start_date = models.DateField(primary_key=True)
    billing_end_date = models.DateField()
    bill_month = models.DateField()
    billing_days = models.IntegerField()
    prior_excess_generation = models.IntegerField()
    contribution = models.IntegerField()
    useage = models.IntegerField()
    billed_useage = models.IntegerField()
    billed_amount = models.FloatField()
    avg_daily_temp = models.IntegerField() # trim the degree symbol
    avg_daily_use = models.IntegerField()
    basic_service_charge = models.FloatField()
    theoretical_charge = models.FloatField()
    theoretical_savings = models.FloatField()
    price_per_kwh = models.FloatField()
    actual_price_per_kwh = models.FloatField(null=True)

class EnergyUse(models.Model):
    id = models.TextField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    main_panel_1 = models.FloatField()
    main_panel_2 = models.FloatField()
    air_conditioner = models.FloatField()
    feed_room = models.FloatField()
    south_stalls = models.FloatField()
    north_stalls = models.FloatField()
    garage = models.FloatField()
    solar_1 = models.FloatField()
    solar_2 = models.FloatField()
    furnace = models.FloatField()
    stall_lighting = models.FloatField()
    rear_exterior = models.FloatField()
    tack_room = models.FloatField()
    stairs = models.FloatField()
    water_heater = models.FloatField()
    front_exterior = models.FloatField()
    whirlpool = models.FloatField()
    barn_bathroom = models.FloatField()
    ### sub panel
    sub_panel_1 = models.FloatField()
    sub_panel_2 = models.FloatField()
    office_1 = models.FloatField()
    stove = models.FloatField()
    microwave = models.FloatField()
    bedrooms = models.FloatField()
    main_half_bath = models.FloatField()
    laundry = models.FloatField()
    master_bathroom = models.FloatField()
    kitchen_1 = models.FloatField()
    kitchen_2 = models.FloatField()
    bath_lighting = models.FloatField()
    deck = models.FloatField()
    living_room = models.FloatField()
    refrigerator = models.FloatField()
    dishwasher = models.FloatField()
    office_den_kitchen = models.FloatField()
    laundry_storage_pantry = models.FloatField()


class SolarGeneration(models.Model):
    id = models.TextField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    generationWh = models.FloatField(null=True)
    generationKwh = models.FloatField(null=True)