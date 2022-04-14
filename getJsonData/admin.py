from django.contrib import admin

# Register your models here.
from .models import Country, Source, Data

admin.site.register(Country)
admin.site.register(Source)
admin.site.register(Data)