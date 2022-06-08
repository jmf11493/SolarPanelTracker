from django.shortcuts import render,redirect
from django.db.models import Sum, Count
from django.db.models.functions import Trunc
from .models import WeatherHistory, EnergyBill, WeatherObservations, SunData, EnergyUse, SolarGeneration
import xml.etree.ElementTree as ET
import requests
import datetime
import logging
import uuid
import json
import itertools
import os
# from builtins import None

solarFileDataPath = ""
mainPanelCsv = ""
subPanelCsv = ""
siteId = ""
apiKey = ""
weatherFileDataPath = ""
config_file_path = os.getcwd() + '\config.csv'

with open(config_file_path,'r') as config_file:
    contents = config_file.read()
    data = contents.split(',')
    solarFileDataPath = data[0]
    weatherFileDataPath = data[0]
    mainPanelCsv = data[1]
    subPanelCsv = data[2]
    siteId = data[3]
    apiKey = data[4]
# Create your views here.
def index(request):
#     sun_data = SunData.objects.all()
#     weather_hist = WeatherHistory.objects.all()
#
#     bills = EnergyBill.objects.all()

# TODO projections for future bill
    all_bills = EnergyBill.objects.order_by('-billing_start_date')
    latest_bill = EnergyBill.objects.order_by('-billing_start_date')[0]

    date_start = latest_bill.billing_start_date
    date_end = latest_bill.billing_end_date

    day_before_start = date_start - datetime.timedelta(1)

    previous_bill = EnergyBill.objects.order_by('-billing_start_date')[1]
    date_previous_start = previous_bill.billing_start_date
    date_previous_end = previous_bill.billing_end_date

    weather_history_range = WeatherHistory.objects.filter(date__range=[date_start, date_end])
    sun_data = SunData.objects.filter(date__range=[date_start, date_end])
    generation = SolarGeneration.objects.filter(date__range=[day_before_start, date_end]).values('date').annotate(total=Sum('generationKwh'))
    total_gen = SolarGeneration.objects.filter(date__range=[day_before_start, date_end]).aggregate(Sum('generationKwh'))

    previous_weather_history_range = WeatherHistory.objects.filter(date__range=[date_previous_start, date_previous_end])
    previous_sun_data = SunData.objects.filter(date__range=[date_previous_start, date_previous_end])
    previous_generation = SolarGeneration.objects.filter(date__range=[date_previous_start, date_previous_end]).values('date').annotate(total=Sum('generationKwh'))
    previous_total_gen = SolarGeneration.objects.filter(date__range=[date_previous_start, date_previous_end]).aggregate(Sum('generationKwh'))

    conditions = []
    obs_date = date_start

    while obs_date != date_end:
        observations = WeatherObservations.objects.filter(date=obs_date).values('condition')
        weather_summary = []
        for condition in observations:
            weather_summary.append(condition['condition'].split('\n')[0])
        short_summary = []
        for index, weather in enumerate(weather_summary):
            if index == 0:
                short_summary.append(weather)
                continue
            prev = index - 1
            previous = weather_summary[prev]
            if previous != weather:
                short_summary.append(weather)
        obs_date += datetime.timedelta(days=1)
        conditions.append(', '.join(short_summary))
    test_sql = zip(sun_data, generation, conditions)
    count = 'sun_data: ' + str(sun_data.count()) + ' gen_data: ' + str(generation.count())
#     if sun_data.count() == generation.count():
#         test_sql = sun_data.union(generation)



    totals = 0.0
    previous_totals = 0.0
    table_html = ''
    skip = ["main_panel_1", "main_panel_2", "sub_panel_1", "sub_panel_2", "solar_1", "solar_2"]
    room_daily_use = {}
    query_arr = [
        "main_panel_1",
        "main_panel_2",
        "air_conditioner",
        "feed_room",
        "south_stalls",
        "north_stalls",
        "garage",
        "solar_1",
        "solar_2",
        "furnace",
        "stall_lighting",
        "rear_exterior",
        "tack_room",
        "stairs",
        "water_heater",
        "front_exterior",
        "whirlpool",
        "barn_bathroom",
        "sub_panel_1",
        "sub_panel_2",
        "office_1",
        "stove",
        "microwave",
        "bedrooms",
        "main_half_bath",
        "laundry",
        "master_bathroom",
        "kitchen_1",
        "kitchen_2",
        "bath_lighting",
        "deck",
        "living_room",
        "refrigerator",
        "dishwasher",
        "office_den_kitchen",
        "laundry_storage_pantry"
    ]
    results = {}
    for room in query_arr:
        useage = EnergyUse.objects.filter(date__range=[day_before_start, date_end]).aggregate(Sum(room))[room + "__sum"]
        previous_useage = EnergyUse.objects.filter(date__range=[date_previous_start, date_previous_end]).aggregate(Sum(room))[room + "__sum"]
#         daily_use = EnergyUse.objects.filter(date__range=[date_start, date_end]).values('date').annotate(total=Sum(room))
#         room_daily_use[room] = daily_use
        results[room] = round(useage,1)
        results['p_' + room] = round(previous_useage,1)
        proper_title = ''
        for word in room.split('_'):
            proper_title = proper_title + word.capitalize() + ' '
        table_html = table_html + '<tr><td>' + proper_title + '</td><td>' + str(useage) + '</td></tr>'
        if room not in skip:
            totals = totals + useage
            previous_totals = previous_totals + previous_useage

#     query where date is greater or equal to the start date of the billing cycle
    results["bill"] = latest_bill
    results["bills"] = all_bills
    results["previous_bill"] = previous_bill
    results["sun_data"] = sun_data
    results["weather_hist"] = weather_history_range
    results["generation"] = generation
    results["total_generation"] = total_gen
    results["previous_total_generation"] = previous_total_gen
    results["total_useage"] = totals
    results["previous_total_useage"] = previous_totals
    results["table_html"] = table_html
    results["test_sql"] = test_sql
    results["observation"] = conditions
    results["count"] = count
#     results["room_daily_use"] = room_daily_use
    results["average_daily_use"] = totals / int(latest_bill.billing_days)
    results["previous_average_daily_use"] = previous_totals / int(previous_bill.billing_days)

    return render(request, 'dashboard/index.html', results)

def updateCircuitBreakers(request):
#     EnergyUse.objects.all().delete()
    logger = logging.getLogger('test')

    mainpanel = solarFileDataPath + mainPanelCsv
    subpanel = solarFileDataPath + subPanelCsv

    main_panel_file = open(mainpanel, 'r')
    sub_panel_file = open(subpanel, 'r')

    combined_energy_use = solarFileDataPath + 'combined_energy_use.txt'
    energy_file = open(combined_energy_use, "a")

    line_count = 0
    for (main_line, sub_line) in zip(main_panel_file, sub_panel_file):
        line_count += 1
        if line_count == 1:
            continue
        main_data = main_line.split(',')
        main_date = main_data[0]

        date_time = main_date.split(' ')
        main_date = date_time[0].split('/')
        main_date = datetime.date(int(main_date[2]), int(main_date[0]), int(main_date[1]))
        main_time = date_time[1].split(':')
        main_time = datetime.time(int(main_time[0]), int(main_time[1]), 0)

        main_panel_1 = convertToFloat(main_data[1])
        main_panel_2 = convertToFloat(main_data[2])
        # this column probably won't exist in future file dumps
        # main_panel_3 = convertToFloat(main_data[3])
        air_conditioner = convertToFloat(main_data[3])
        feed_room = convertToFloat(main_data[4])
        south_stalls = convertToFloat(main_data[5])
        north_stalls = convertToFloat(main_data[6])
        garage = convertToFloat(main_data[7])
        solar_1 = convertToFloat(main_data[8])
        solar_2 = convertToFloat(main_data[9])
        furnace = convertToFloat(main_data[10])
        stall_lighting = convertToFloat(main_data[11])
        rear_exterior = convertToFloat(main_data[12])
        tack_room = convertToFloat(main_data[13])
        stairs = convertToFloat(main_data[14])
        water_heater = convertToFloat(main_data[15])
        front_exterior = convertToFloat(main_data[16])
        whirlpool = convertToFloat(main_data[17])
        barn_bathroom = convertToFloat(main_data[18])


        sub_data = sub_line.split(',')
        sub_date = sub_data[0]
        sub_date_time = sub_date.split(' ')
        sub_date = sub_date_time[0].split('/')
        sub_date = datetime.date(int(sub_date[2]), int(sub_date[0]), int(sub_date[1]))
        sub_time = sub_date_time[1].split(':')
        sub_time = datetime.time(int(sub_time[0]), int(sub_time[1]), 0)

        sub_panel_1 = convertToFloat(sub_data[1])
        sub_panel_2 = convertToFloat(sub_data[2])
        office_1 = convertToFloat(sub_data[3])
        stove = convertToFloat(sub_data[4])
        microwave = convertToFloat(sub_data[5])
        bedrooms = convertToFloat(sub_data[6])
        main_half_bath = convertToFloat(sub_data[7])
        laundry = convertToFloat(sub_data[8])
        master_bathroom = convertToFloat(sub_data[9])
        kitchen_1 = convertToFloat(sub_data[10])
        kitchen_2 = convertToFloat(sub_data[11])
        bath_lighting = convertToFloat(sub_data[12])
        deck = convertToFloat(sub_data[13])
        living_room = convertToFloat(sub_data[14])
        refrigerator = convertToFloat(sub_data[15])
        dishwasher = convertToFloat(sub_data[16])
        office_den_kitchen = convertToFloat(sub_data[17])
        laundry_storage_pantry = convertToFloat(sub_data[18])

        if sub_date == main_date and sub_time == main_time:
            uid = str(main_date) + '-' + str(main_time)
            try:
                result = EnergyUse.objects.get(id = uid)
            except:
                result = None
            if not result:
                eU = EnergyUse(
                    uid,
                    main_date,
                    main_time,
                    main_panel_1,
                    main_panel_2,
                    air_conditioner,
                    feed_room,
                    south_stalls,
                    north_stalls,
                    garage,
                    solar_1,
                    solar_2,
                    furnace,
                    stall_lighting,
                    rear_exterior,
                    tack_room,
                    stairs,
                    water_heater,
                    front_exterior,
                    whirlpool,
                    barn_bathroom,
                    sub_panel_1,
                    sub_panel_2,
                    office_1,
                    stove,
                    microwave,
                    bedrooms,
                    main_half_bath,
                    laundry,
                    master_bathroom,
                    kitchen_1,
                    kitchen_2,
                    bath_lighting,
                    deck,
                    living_room,
                    refrigerator,
                    dishwasher,
                    office_den_kitchen,
                    laundry_storage_pantry
                )
                eU.save()
        else:
            logger.warn('Conflicting date time stamps for files')
    return redirect('dashboard')
def convertToFloat(data):
    if data == 'No CT':
        data = 0.0
    else:
        data = float(data)
    return data

def updateWeatherHistory(request):
    logger = logging.getLogger('test')

    weatherHistory = 'Weather_History.txt'
    weatherSunData = 'Weather_Sun_Data.txt'
    weatherObservations = 'Weather_Observations.txt'

    files = [
        weatherHistory,
        weatherSunData,
        weatherObservations
    ]

    for file in files:
        logger.warning('file: ' + file)
        filePath = solarFileDataPath + file
        fileOpen = open(filePath, "r")
        lines = fileOpen.readlines()

        lineCount = 0
        for line in lines:
            data_array = line.split(",")

            if file == weatherHistory:
                whDate = data_array[0].split('-')
                logger.warning('Date: ' + whDate[0] + '/' + whDate[1] + '/' + whDate[2])
                whDate = datetime.date(int(whDate[0]), int(whDate[1]), int(whDate[2]))
                actual = data_array[2]
                avg = data_array[3]
                record = data_array[4].replace('\n', '')
                if actual == '-':
                    actual = None
                else:
                    actual = float(actual)
                if avg == '-':
                    avg = None
                else:
                    avg = float(avg)
                if record == '-' or record == '--':
                    record = None
                else:
                    record = float(record)
                try:
                    result = WeatherHistory.objects.get(date = whDate)
                except:
                    result = None
                if not result:
                    wH = WeatherHistory(
                        uuid.uuid4(),
                        whDate,
                        str(data_array[1]),
                        actual,
                        avg,
                        record
                    )
                    wH.save()
                # create weatherHistory model
            if file == weatherSunData:
                wsDate = data_array[0].split('-')
                wsDate = datetime.date(int(wsDate[0]), int(wsDate[1]), int(wsDate[2]))
                rise = data_array[2].replace(' AM', '').split(':')
                setTime = data_array[3].replace(' PM', '').split(':')
                hoursTimeMinutes = str(data_array[1]).replace('h', '').replace('m','').split(' ')
                hoursTimeMinutes = int(hoursTimeMinutes[0])*60 + int(hoursTimeMinutes[1])
                try:
                    result = SunData.objects.get(date = wsDate)
                except:
                    result = None
                if not result:
                    wSD = SunData(
                        wsDate,
                        hoursTimeMinutes,
                        datetime.time(int(rise[0]),int(rise[1]),0),
                        datetime.time(int(setTime[0])+12,int(setTime[1]),0),
                    )
                    wSD.save()
                    # create sun data model
            if file == weatherObservations:
                times = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
                primary_key = data_array[0] + str(times[lineCount])
                logger.warn('Observation Date: ' + primary_key)
                woDate = data_array[0].split('-')
                woDate = datetime.date(int(woDate[0]), int(woDate[1]), int(woDate[2]))
                woTime = data_array[1].split(':')
                woTime = datetime.time(int(woTime[0]), int(woTime[1][0:1]), 0)
                try:
                    result = WeatherObservations.objects.get(id = primary_key)
                except:
                    result = None
                if not result:
                    wO = WeatherObservations(
                        primary_key,
                        woDate,
                        datetime.time(times[lineCount], 0, 0), # corrected time
                        woTime,
                        int(data_array[2]),
                        int(data_array[3]),
                        int(data_array[4]),
                        str(data_array[5]),
                        int(data_array[6]),
                        int(data_array[7]),
                        float(data_array[8]),
                        float(data_array[9]),
                        str(data_array[10])
                    )
                    wO.save()
                lineCount+=1
                if lineCount > 23:
                    lineCount = 0
    return redirect('dashboard')

def updateNysegBills(request):
#     EnergyBill.objects.all().delete()
    logger = logging.getLogger('test')
    nysegBills = 'NYSEG_Bills.txt'

    logger.warning('file: ' + nysegBills)
    filePath = solarFileDataPath + nysegBills
    fileOpen = open(filePath, "r")
    lines = fileOpen.readlines()

    for line in lines:
        data_array = line.split(",")
        logger.warning('nyseg bill')
        billing_dates = data_array[1].split(" - ")
        billing_start_date = billing_dates[0].split("/")
        billing_start_date = datetime.date(int(billing_start_date[2])+2000, int(billing_start_date[0]), int(billing_start_date[1]))
        billing_end_date = billing_dates[1].split("/")
        billing_end_date = datetime.date(int(billing_end_date[2])+2000, int(billing_end_date[0]), int(billing_end_date[1]))
        logger.warning('nyseg bill dates: ' + str(billing_start_date) + ' ' + str(billing_end_date))
        try:
            result = EnergyBill.objects.get(billing_start_date = billing_start_date)
        except:
            result = None
        if not result:
            logger.warning('add energy bill entry')
            actual_ppkwh = data_array[15]
            if "\n" in actual_ppkwh:
                actual_ppkwh = actual_ppkwh.replace("\n", "")
            if actual_ppkwh == "n/a":
                actual_ppkwh = None
            else:
                actual_ppkwh = float(actual_ppkwh)
            eB = EnergyBill(
                billing_start_date,
                billing_end_date,
                billing_end_date, #billing end date is the bill month
                int(data_array[2]),
                int(data_array[4]),
                int(data_array[5]),
                int(data_array[6]),
                int(data_array[7]),
                float(data_array[8]),
                int(data_array[9][:-1]), #strip the degree symbol
                int(data_array[10]),
                float(data_array[11]),
                float(data_array[12]),
                float(data_array[13]),
                float(data_array[14]),
                actual_ppkwh
            )
            eB.save()
    return redirect('dashboard')
def updateSolarPanels(request):
    logger = logging.getLogger('test')
    start_year = 2022
    start_month = 4
    start_day = 11
    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(2022, 6, 1)
    # 2022 - 3 - 16 last day with good data
    # if we go into the future all values will be null
    range1 = start_date
    solarFile = solarFileDataPath + 'solar_data.txt'
    file = open(solarFile, "a")
    while range1 < end_date:
        start_month += 1
        if start_month > 12:
            start_month -= 12
            start_year += 1
        range2 = datetime.date(start_year, start_month, start_day)

        # check if end date is in the database first
        try:
            result = SolarGeneration.objects.get(date = range2)
        except:
            result = None
        if not result:
            url = 'https://monitoringapi.solaredge.com/site/'+siteId+'/energy?timeUnit=HOUR&startDate='+str(range1)+'&endDate='+str(range2)+'&api_key='+apiKey
            response = requests.get(url)
            json_data = json.loads(response.text)
            values = json_data.get('energy').get('values')
            for dataValue in values:
                dateTimeStr = dataValue.get('date').split()
                value = dataValue.get('value')
                dateStr = dateTimeStr[0].split("-")
                timeStr = dateTimeStr[1].split(":")

                year = int(dateStr[0])
                month = int(dateStr[1])
                day = int(dateStr[2])

                hour = int(timeStr[0])
                minute = int(timeStr[1])
                second = int(timeStr[2])

                date = datetime.date(year, month, day)
                time = datetime.time(hour, minute, second)

                generationWh = None
                generationKwh = None

                if date > end_date:
                    break

                if value != None:
                    generationWh = value
                    generationKwh = generationWh / 1000.0
                try:
                    result = SolarGeneration.objects.get(date = date, time = time)
                except:
                    result = None
                if not result:
                    uid = str(date) + ' ' + str(time)
                    line = str(uid) + ',' + str(generationWh) + ',' + str(generationKwh) + '\n'
                    logger.warning('Writing solar data: ' + line)
                    file.write(line)
                    sG = SolarGeneration(
                        uid,
                        date,
                        time,
                        generationWh,
                        generationKwh
                    )
                    sG.save()

        range1 = range2
    file.close()
    return redirect('dashboard')
def updateDatabase(request):
    logger = logging.getLogger('test')
    weatherHistory = 'Weather_History.txt'
    weatherSunData = 'Weather_Sun_Data.txt'
    weatherObservations = 'Weather_Observations.txt'
    nysegBills = 'NYSEG_Bills.txt'
    mainpanel = 'Main_panel.csv'
    subpanel = 'Sub_panel.csv'

    files = [
#             weatherHistory,
#             weatherSunData,
#             weatherObservations,
#             nysegBills
        ]

    # get generation
    # start date 2020-07-02
    # end date 2022-03-12
    start_year = 2020
    start_month = 7
    start_day = 2
    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(2022, 3, 12)
    range1 = start_date
    while range1 < end_date:
        start_month += 1
        if start_month > 12:
            start_month -= 12
            start_year += 1
        range2 = datetime.date(start_year, start_month, start_day)

        # check if end date is in the database first
        try:
            result = SolarGeneration.objects.get(date = range2)
        except:
            result = None
        if not result:
            url = 'monitoringapi.solaredge.com/site/'+siteId+'/energy?timeUnit=HOUR&startDate='+str(range1)+'&endDate='+str(range2)+'&api_key='+apiKey
            response = requests.get(url)
            root = ET.parse(response)
            values = root[3]
            for dataValue in values:
                dateTimeStr = dataValue[0].text.split()
                value = dataValue[1].text

                dateStr = dateTimeStr[0].split("-")
                timeStr = dateTimeStr[1].split(":")

                year = int(dateStr[0])
                month = int(dateStr[1])
                day = int(dateStr[2])

                hour = int(timeStr[0])
                minute = int(timeStr[1])
                second = int(timeStr[2])

                date = datetime.date(year, month, day)
                time = datetime.time(hour, minute, second)

                generationWh = None
                generationKwh = None

                if value != "null":
                    generationWh = float(value)
                    generationKwh = generationWh / 1000.0
                try:
                    result = SolarGeneration.objects.get(date = date, time = time)
                except:
                    result = None
                if not result:
                    sG = SolarGeneration(
                        uuid.uuid4(),
                        date,
                        time,
                        generationWh,
                        generationKwh
                    )
                    sG.save()

        range1 = range2



    for file in files:
        logger.warning('file: ' + file)
        filePath = weatherFileDataPath + file
        fileOpen = open(filePath, "r")
        lines = fileOpen.readlines()

        lineCount = 0
        for line in lines:
            data_array = line.split(",")
            if file == mainpanel or file == subpanel:
                # do something
                i = 1
            if file == nysegBills:
                logger.warning('nyseg bill')
                billing_dates = data_array[1].split(" - ")
                billing_start_date = billing_dates[0].split("/")
                billing_start_date = datetime.date(int(billing_start_date[2])+2000, int(billing_start_date[0]), int(billing_start_date[1]))
                billing_end_date = billing_dates[1].split("/")
                billing_end_date = datetime.date(int(billing_end_date[2])+2000, int(billing_end_date[0]), int(billing_end_date[1]))
                logger.warning('nyseg bill dates: ' + str(billing_start_date) + ' ' + str(billing_end_date))
                try:
                    result = EnergyBill.objects.get(billing_start_date = billing_start_date)
                except:
                    result = None
                if not result:
                    logger.warning('add energy bill entry')
                    eB = EnergyBill(
                        billing_start_date,
                        billing_end_date,
                        billing_end_date, #billing end date is the bill month
                        int(data_array[2]),
                        int(data_array[4]),
                        int(data_array[5]),
                        int(data_array[6]),
                        int(data_array[7]),
                        float(data_array[8]),
                        int(data_array[9][0:1]),
                        int(data_array[10]),
                        float(data_array[11]),
                        float(data_array[12]),
                        float(data_array[13]),
                        float(data_array[14])
                    )
                    eB.save()
            if file == weatherHistory:
                whDate = data_array[0].split('-')
                logger.warning('Date: ' + whDate[0] + '/' + whDate[1] + '/' + whDate[2])
                whDate = datetime.date(int(whDate[0]), int(whDate[1]), int(whDate[2]))
                actual = data_array[2]
                avg = data_array[3]
                record = data_array[4].replace('\n', '')
                if actual == '-':
                    actual = None
                else:
                    actual = float(actual)
                if avg == '-':
                    avg = None
                else:
                    avg = float(avg)
                if record == '-' or record == '--':
                    record = None
                else:
                    record = float(record)
                try:
                    result = WeatherHistory.objects.get(date = whDate)
                except:
                    result = None
                if not result:
                    wH = WeatherHistory(
                        uuid.uuid4(),
                        whDate,
                        str(data_array[1]),
                        actual,
                        avg,
                        record
                    )
                    wH.save()
                # create weatherHistory model
            if file == weatherSunData:
                wsDate = data_array[0].split('-')
                wsDate = datetime.date(int(wsDate[0]), int(wsDate[1]), int(wsDate[2]))
                rise = data_array[2].replace(' AM', '').split(':')
                setTime = data_array[3].replace(' PM', '').split(':')
                hoursTimeMinutes = str(data_array[1]).replace('h', '').replace('m','').split(' ')
                hoursTimeMinutes = int(hoursTimeMinutes[0])*60 + int(hoursTimeMinutes[1])
                try:
                    result = SunData.objects.get(date = wsDate)
                except:
                    result = None
                if not result:
                    wSD = SunData(
                        wsDate,
                        hoursTimeMinutes,
                        datetime.time(int(rise[0]),int(rise[1]),0),
                        datetime.time(int(setTime[0])+12,int(setTime[1]),0),
                    )
                    wSD.save()
                    # create sun data model
            if file == weatherObservations:
                times = [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23
                ]
                primary_key = data_array[0] + str(times[lineCount])
                logger.warn('Observation Date: ' + primary_key)
                woDate = data_array[0].split('-')
                woDate = datetime.date(int(woDate[0]), int(woDate[1]), int(woDate[2]))
                woTime = data_array[1].split(':')
                woTime = datetime.time(int(woTime[0]), int(woTime[1][0:1]), 0)
                try:
                    result = WeatherObservations.objects.get(id = primary_key)
                except:
                    result = None
                if not result:
                    wO = WeatherObservations(
                        primary_key,
                        woDate,
                        datetime.time(times[lineCount], 0, 0), # corrected time
                        woTime,
                        int(data_array[2]),
                        int(data_array[3]),
                        int(data_array[4]),
                        str(data_array[5]),
                        int(data_array[6]),
                        int(data_array[7]),
                        float(data_array[8]),
                        float(data_array[9]),
                        str(data_array[10])
                    )
                    wO.save()
                lineCount+=1
                if lineCount > 23:
                    lineCount = 0
    # open file
    # read by line
    # string split by ,
    return redirect('dashboard')
#     https://www.solaredge.com/sites/default/files//se_monitoring_api.pdf
#
# Use of the monitoring server API is subject to a query limit of 300 requests for a specific account token and a parallel query limit
# of 300 requests for each specific site ID from the same source IP.

