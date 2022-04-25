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
from .models import Area, PsrType, Data, ProcessType, DayAheadData, DocumentType, DayAheadPriceData, \
    NasdaqODAPALUMUSD, NasdaqODAPCOPPUSD, NasdaqSHFERBV2013, NasdaqODAPNICKUSD, NasdaqJOHNMATTPLAT, NasdaqJOHNMATTPALL

base_path = Path(os.path.abspath(__file__)).parents[2]


class MainPage(View):
    def get(self, response):
        info = "You need to open url: " \
               "<br> 1. http://domain/day_ahead/{{area}}" \
               "<br> 2. http://domain/day_ahead_price/{{area}}" \
               "<br> 3. http://domain/source/{{area}}/{{code_source}}" \
               "<br><br> nasdaq" \
               "<br> 1. http://domain/nasdaq/{{resource}}" \
               "<pre>   <strong> 1.1. ODA_PALUM_USD</strong> - Aluminum</pre>" \
               "<pre>   <strong> 1.2. ODA_PCOPP_USD</strong> - Copper</pre>" \
               "<pre>   <strong> 1.3. SHFE_RBV2013</strong> - Shanghai Steel Rebar Futures</pre>" \
               "<pre>   <strong> 1.4. ODA_PNICK_USD</strong> - Nickel</pre>" \
               "<pre>   <strong> 1.5. JOHNMATT_PLAT</strong> - Platinum, Johnson Mathey London</pre>" \
               "<pre>   <strong> 1.6. JOHNMATT_PALL</strong> - Palladium, Johnson Mathey London</pre>"

        return HttpResponse(info)


class GetCountryData(View):
    def get(self, request, area, psrType):
        current_year = datetime.now().year
        # print(F"base_path = {base_path}")
        # files_path = str(base_path) + '\cron\data\years\\'
        files_path = str(base_path) + '/cron/data/years/psrType/'

        response_data = {'area': area, 'psrType': psrType}
        # print(files_path)

        data = Area.objects.filter(area=area).count()

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

                    # print(F"period_start = {period_start}")

                    if Area.objects.filter(area=area).count() == 0:
                        p = Area(area=area)
                        p.save()

                    area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
                    psrType_count = PsrType.objects.filter(
                        area=area_id,
                        psrType=psrType,
                    ).count()

                    if psrType_count == 0:
                        p = PsrType(
                            area=Area.objects.get(pk=area_id),
                            psrType=psrType
                        )
                        p.save()

                    count_index = 0
                    quantity = 0
                    tz = dict_file['tz']

                    local_tz = pytz.timezone(tz)
                    period_start = local_tz.localize(period_start)

                    for x in point:
                        quantity += int(x['quantity'])
                        count_index += 1
                        if count_index == 4:
                            period_start = period_start + timedelta(hours=1)

                            source_id = PsrType.objects.filter(
                                area=area_id,
                                psrType=psrType,
                            ).values_list('id', flat=True)[0]

                            data_id = Data.objects.filter(
                                psrType=PsrType.objects.get(pk=source_id),
                                datetime=period_start,
                            ).values_list('id', flat=True)

                            if len(data_id) == 0:
                                p = Data(
                                    psrType=PsrType.objects.get(pk=source_id),
                                    datetime=period_start,
                                    data=quantity / 4
                                )
                                p.save()
                            quantity = 0
                            count_index = 0
                        # print(F"x = {x}")
                os.remove(files_path + file)

        data = self.getDataFromDB(area, psrType)

        # response_data['data'] = serializers.serialize("json", data)

        if data == 'none':
            response_data['data'] = data
        else:
            for item in list(data):
                item['date'] = item['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")
                item.pop('datetime')
            response_data['data'] = list(data)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getDataFromDB(self, area, psrType):
        try:
            area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
        except:
            return 'none'
        source_id = PsrType.objects.filter(
            area=area_id,
            psrType=psrType,
        ).values_list('id', flat=True)[0]
        data = Data.objects.filter(
            psrType=PsrType.objects.get(pk=source_id),
        ).values('id', 'datetime', 'data').order_by('datetime')
        return data


class GetDayAheadData(View):
    def get(self, request, area):
        current_year = datetime.now().year
        # print(F"base_path = {base_path}")
        # files_path = str(base_path) + '\cron\data\years\day_ahead\\'
        files_path = str(base_path) + '/cron/data/years/day_ahead/'

        response_data = {'area': area}
        dir_list = os.listdir(files_path)
        for file in dir_list:

            with open(files_path + file) as f:
                dict_file = json.loads(f.read())

                tz = dict_file['tz']

                for day in dict_file['GL_MarketDocument']['TimeSeries']:
                    area = day['outBiddingZone_Domain.mRID']['#text']
                    process_type = day['outBiddingZone_Domain.mRID']['@codingScheme']
                    if Area.objects.filter(area=area).count() == 0:
                        p = Area(area=area)
                        p.save()

                    area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
                    obj_process_type = ProcessType.objects.filter(
                        area=area_id,
                        process_type=process_type,
                    ).count()

                    if obj_process_type == 0:
                        p = ProcessType(
                            area=Area.objects.get(pk=area_id),
                            process_type=process_type
                        )
                        p.save()

                    local_tz = pytz.timezone(tz)
                    period_start = datetime.strptime(
                        day['Period']['timeInterval']['start'],
                        "%Y-%m-%dT%H:%MZ"
                    )
                    period_start = local_tz.localize(period_start)
                    count_index = 0
                    quantity = 0

                    for data in day['Period']['Point']:
                        quantity += int(data['quantity'])
                        count_index += 1
                        if count_index == 4:
                            period_start = period_start + timedelta(hours=1)

                            id_process_type = ProcessType.objects.filter(
                                area=area_id,
                                process_type=process_type
                            ).values_list('id', flat=True)[0]

                            data_id = DayAheadData.objects.filter(
                                process_type=ProcessType.objects.get(pk=id_process_type),
                                datetime=period_start,
                            ).values_list('id', flat=True)

                            if len(data_id) == 0:
                                p = DayAheadData(
                                    process_type=ProcessType.objects.get(pk=id_process_type),
                                    datetime=period_start,
                                    data=quantity
                                )
                                p.save()
                            quantity = 0
                            count_index = 0
            os.remove(files_path + file)

        data = self.getDataDayAhead(area, 'A01')

        # print(data)

        # response_data['data'] = serializers.serialize("json", data)

        if data == 'none':
            response_data['data'] = data
        else:
            for item in list(data):
                item['date'] = item['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")
                item.pop('datetime')
            response_data['data'] = list(data)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getDataDayAhead(self, area, process_type):
        try:
            area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
        except:
            return 'none'
        process_type_id = ProcessType.objects.filter(
            area=area_id,
            process_type=process_type
        ).values_list('id', flat=True)[0]
        data = DayAheadData.objects.filter(
            process_type=ProcessType.objects.get(pk=process_type_id),
        ).values('id', 'datetime', 'data').order_by('datetime')
        return data


class GetDayAheadPriceData(View):
    def get(self, request, area):
        current_year = datetime.now().year
        # print(F"base_path = {base_path}")
        # files_path = str(base_path) + '\cron\data\years\day_ahead\\'
        files_path = str(base_path) + '/cron/data/years/day_ahead_price/'

        response_data = {'area': area}
        # print(files_path)

        # data = Area.objects.filter(area=area).count()

        # if data == 0:
        dir_list = os.listdir(files_path)
        for file in dir_list:

            with open(files_path + file) as f:
                dict_file = json.loads(f.read())

                tz = dict_file['tz']

                for day in dict_file['Publication_MarketDocument']['TimeSeries']:
                    area = day['in_Domain.mRID']['#text']
                    document_type = day['in_Domain.mRID']['@codingScheme']
                    if Area.objects.filter(area=area).count() == 0:
                        p = Area(area=area)
                        p.save()

                    area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
                    obj_process_type = DocumentType.objects.filter(
                        area=area_id,
                        document_type=document_type,
                    ).count()

                    if obj_process_type == 0:
                        p = DocumentType(
                            area=Area.objects.get(pk=area_id),
                            document_type=document_type
                        )
                        p.save()

                    local_tz = pytz.timezone(tz)
                    period_start = datetime.strptime(
                        day['Period']['timeInterval']['start'],
                        "%Y-%m-%dT%H:%MZ"
                    )
                    period_start = local_tz.localize(period_start)

                    for data in day['Period']['Point']:
                        period_start = period_start + timedelta(hours=1)

                        id_process_type = DocumentType.objects.filter(
                            area=area_id,
                            document_type=document_type
                        ).values_list('id', flat=True)[0]

                        data_id = DayAheadPriceData.objects.filter(
                            document_type=DocumentType.objects.get(pk=id_process_type),
                            datetime=period_start,
                        ).values_list('id', flat=True)

                        if len(data_id) == 0:
                            p = DayAheadPriceData(
                                document_type=DocumentType.objects.get(pk=id_process_type),
                                datetime=period_start,
                                data=data['price.amount']
                            )
                            p.save()
                        # print(F"quantity = {quantity} | count = {count}")
            os.remove(files_path + file)

        data = self.getDataDayAheadPrice(area, 'A01')

        # print(data)

        # response_data['data'] = serializers.serialize("json", data)

        if data == 'none':
            response_data['data'] = data
        else:
            for item in list(data):
                item['date'] = item['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")
                item.pop('datetime')
            response_data['data'] = list(data)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getDataDayAheadPrice(self, area, document_type):
        print(F"area = {area}, type = {document_type}")
        try:
            area_id = Area.objects.filter(area=area).values_list('id', flat=True)[0]
        except:
            return 'none'
        process_type_id = DocumentType.objects.filter(
            area=area_id,
            document_type=document_type
        ).values_list('id', flat=True)[0]
        data = DayAheadPriceData.objects.filter(
            document_type=DocumentType.objects.get(pk=process_type_id),
        ).values('id', 'datetime', 'data').order_by('datetime')
        return data


class GetNasdaqData(View):
    def get(self, request, resource):
        files_path = str(base_path) + '/cron/data/nasdaq/'

        # response_data = {'area': area}
        dir_list = os.listdir(files_path)
        for file in dir_list:
            remove = False
            with open(files_path + file) as f:
                dict_file = json.loads(f.read())

                if dict_file['dataset']['database_code'] + '_' + dict_file['dataset']['dataset_code'] == resource:
                    print(F"resource = {resource}")
                    if resource == 'ODA_PALUM_USD':
                        self.set_ODA_PALUM_USD(dict_file)
                        remove = True
                    elif resource == 'ODA_PCOPP_USD':
                        self.set_ODA_PCOPP_USD(dict_file)
                        remove = True
                    elif resource == 'SHFE_RBV2013':
                        self.set_SHFE_RBV2013(dict_file)
                        remove = True
                    elif resource == 'ODA_PNICK_USD':
                        self.set_ODA_PNICK_USD(dict_file)
                        remove = True
                    elif resource == 'JOHNMATT_PLAT':
                        self.set_JOHNMATT_PLAT(dict_file)
                        remove = True
                    elif resource == 'JOHNMATT_PALL':
                        self.set_JOHNMATT_PALL(dict_file)
                        remove = True

            if remove:
                 os.remove(files_path + file)

        if resource == 'ODA_PALUM_USD':
            data = self.get_ODA_PALUM_USD()
        elif resource == 'ODA_PCOPP_USD':
            data = self.get_ODA_PCOPP_USD()
        elif resource == 'SHFE_RBV2013':
            data = self.get_SHFE_RBV2013()
        elif resource == 'ODA_PNICK_USD':
            data = self.get_ODA_PNICK_USD()
        elif resource == 'JOHNMATT_PLAT':
            data = self.get_JOHNMATT_PLAT()
        elif resource == 'JOHNMATT_PALL':
            data = self.get_JOHNMATT_PALL()

        if data != 'none':
            for item in list(data):
                item['date'] = item['date'].strftime("%Y-%m-%d")

        return HttpResponse(data, content_type="application/json")

    def set_ODA_PALUM_USD(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqODAPALUMUSD.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqODAPALUMUSD(
                    date=item[0],
                    value=item[1]
                )
                p.save()

    def set_ODA_PCOPP_USD(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqODAPCOPPUSD.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqODAPCOPPUSD(
                    date=item[0],
                    value=item[1]
                )
                p.save()

    def set_SHFE_RBV2013(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqSHFERBV2013.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqSHFERBV2013(
                    date=item[0],
                    pre_settle=item[1],
                    open=item[2],
                    high=item[3],
                    low=item[4],
                    close=item[5],
                    settle=item[6],
                    ch1=item[7],
                    ch2=item[8],
                    volume=item[9],
                    prev=item[10],
                    change=item[11],
                )
                p.save()

    def set_ODA_PNICK_USD(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqODAPNICKUSD.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqODAPNICKUSD(
                    date=item[0],
                    value=item[1]
                )
                p.save()

    def set_JOHNMATT_PLAT(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqJOHNMATTPLAT.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqJOHNMATTPLAT(
                    date=item[0],
                    hong_kong_8_30=item[1],
                    hong_kong_14_00=item[2],
                    london_09_00=item[3],
                    new_york_9_30=item[4]
                )
                p.save()

    def set_JOHNMATT_PALL(self, file):
        for item in file['dataset']['data']:
            obj = NasdaqJOHNMATTPALL.objects.filter(
                date=item[0],
            )
            if obj.count() == 0:
                p = NasdaqJOHNMATTPALL(
                    date=item[0],
                    hong_kong_8_30=item[1],
                    hong_kong_14_00=item[2],
                    london_09_00=item[3],
                    new_york_9_30=item[4]
                )
                p.save()


    def get_ODA_PALUM_USD(self):
        return NasdaqODAPALUMUSD.objects.all().values('id', 'date', 'value').order_by('date')

    def get_ODA_PCOPP_USD(self):
        return NasdaqODAPCOPPUSD.objects.all().values('id', 'date', 'value').order_by('date')

    def get_SHFE_RBV2013(self):
        return NasdaqSHFERBV2013.objects.all().values(
            'id',
            'date',
            'pre_settle',
            'open',
            'high',
            'low',
            'close',
            'settle',
            'ch1',
            'ch2',
            'volume',
            'prev',
            'change'
        ).order_by('date')

    def get_ODA_PNICK_USD(self):
        return NasdaqODAPNICKUSD.objects.all().values('id', 'date', 'value').order_by('date')

    def get_JOHNMATT_PLAT(self):
        return NasdaqJOHNMATTPLAT.objects.all().values(
            'id',
            'date',
            'hong_kong_8_30',
            'hong_kong_14_00',
            'london_09_00',
            'new_york_9_30'
        ).order_by('date')

    def get_JOHNMATT_PALL(self):
        return NasdaqJOHNMATTPALL.objects.all().values(
            'id',
            'date',
            'hong_kong_8_30',
            'hong_kong_14_00',
            'london_09_00',
            'new_york_9_30'
        ).order_by('date')