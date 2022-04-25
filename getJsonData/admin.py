from django.contrib import admin

# Register your models here.
from .models import Area, PsrType, Data

admin.site.register(Area)
admin.site.register(PsrType)
admin.site.register(Data)