import os
from datetime import datetime, timedelta
from pathlib import Path
import json

import pytz as pytz
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from .models import Country, Source, Data

base_path = Path(os.path.abspath(__file__)).parents[2]


class MainPage(View):
    def get(self, response):
        return HttpResponse('You need to open url: <br> http://127.0.0.1:8000/{{country}}/{{code_source}}/')


class GetCountryData(View):
    def get(self, request, areas, source):
        current_year = datetime.now().year
        files_path = str(base_path) + '\cron\data\years\\'

        response_data = {}
        response_data['country'] = areas
        response_data['source'] = source
        print(files_path)

        data = Country.objects.filter(country=areas).count()

        if data == 0:
            dir_list = os.listdir(files_path)
            for file in dir_list:
                with open(files_path + file) as f:
                    dict_file = json.loads(f.read())
                    try:
                        area = dict_file['GL_MarketDocument']['TimeSeries'][0]['inBiddingZone_Domain.mRID']['#text']
                        psrType = dict_file['GL_MarketDocument']['TimeSeries'][0]['MktPSRType']['psrType']
                        period_start = datetime.strptime(
                            dict_file['GL_MarketDocument']['TimeSeries'][0]['Period']['timeInterval']['start'],
                            "%Y-%m-%dT%H:%MZ"
                        )
                        point = dict_file['GL_MarketDocument']['TimeSeries'][0]['Period']['Point']
                        # print('exist')
                    except:
                        area = dict_file['GL_MarketDocument']['TimeSeries']['inBiddingZone_Domain.mRID']['#text']
                        psrType = dict_file['GL_MarketDocument']['TimeSeries']['MktPSRType']['psrType']
                        period_start = datetime.strptime(
                            dict_file['GL_MarketDocument']['TimeSeries']['Period']['timeInterval']['start'],
                            "%Y-%m-%dT%H:%MZ"
                        )
                        point = dict_file['GL_MarketDocument']['TimeSeries']['Period']['Point']
                        # print('not exist')

                    print(F"period_start = {period_start}")

                    if Country.objects.filter(country=area).count() == 0:
                        p = Country(country=area)
                        p.save()

                    area_id = Country.objects.filter(country=area).values_list('id', flat=True)[0]
                    psrType_count = Source.objects.filter(
                        country=area_id,
                        source=psrType,
                    ).count()

                    if psrType_count == 0:
                        p = Source(
                            country=Country.objects.get(pk=area_id),
                            source=psrType
                        )
                        p.save()

                    count_index = 0
                    quantity = 0
                    tz = dict_file['GL_MarketDocument']['time_Period.timeInterval']['tz']

                    local_tz = pytz.timezone(tz)
                    period_start = local_tz.localize(period_start)

                    print(F"tz = {tz}")
                    for x in point:
                        if count_index == 4:
                            period_start = period_start + timedelta(hours=1)

                            source_id = Source.objects.filter(
                                country=area_id,
                                source=psrType,
                            ).values_list('id', flat=True)[0]

                            data_id = Data.objects.filter(
                                source=Source.objects.get(pk=source_id),
                                datetime=period_start,
                            ).values_list('id', flat=True)

                            if len(data_id) == 0:
                                p = Data(
                                    source=Source.objects.get(pk=source_id),
                                    datetime=period_start,
                                    data=quantity / 4
                                )
                                p.save()
                            quantity = 0
                            count_index = 0
                        quantity += int(x['quantity'])
                        count_index += 1
                        # print(F"x = {x}")
                os.remove(files_path + file)

        data = self.getDataFromDB(areas, source)

        # response_data['data'] = serializers.serialize("json", data)

        for item in list(data):
            item['datetime'] = item['datetime'].strftime("%d/%m/%Y, %H:%M:%S")
        print(list(data))
        response_data['data'] = list(data)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getDataFromDB(self, area, source):
        area_id = Country.objects.filter(country=area).values_list('id', flat=True)[0]
        source_id = Source.objects.filter(
            country=area_id,
            source=source,
        ).values_list('id', flat=True)[0]
        data = Data.objects.filter(
            source=Source.objects.get(pk=source_id),
        ).values('id', 'datetime', 'data')
        return data