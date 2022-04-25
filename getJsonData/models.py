from django.db import models


# Create your models here.


class Area(models.Model):
    area = models.CharField('Areas', max_length=100)

    def __str__(self):
        return self.area


class PsrType(models.Model):
    area = models.ForeignKey(Area, verbose_name="Areas", on_delete=models.CASCADE)
    psrType = models.CharField("Source", max_length=150)

    def __str__(self):
        return self.psrType


class Data(models.Model):
    psrType = models.ForeignKey(PsrType, verbose_name="Source", on_delete=models.CASCADE)
    datetime = models.DateTimeField("Datetime")
    data = models.CharField('Data', max_length=200)


class ProcessType(models.Model):
    area = models.ForeignKey(Area, verbose_name="Area", on_delete=models.CASCADE)
    process_type = models.CharField("process type", max_length=150)

    def __str__(self):
        return self.process_type


class DayAheadData(models.Model):
    process_type = models.ForeignKey(ProcessType, verbose_name="process type", on_delete=models.CASCADE)
    datetime = models.DateTimeField("Datetime")
    data = models.CharField('Data', max_length=200)


class DocumentType(models.Model):
    area = models.ForeignKey(Area, verbose_name="Area", on_delete=models.CASCADE)
    document_type = models.CharField('Document Type', max_length=150)

    def __str__(self):
        return self.document_type


class DayAheadPriceData(models.Model):
    document_type = models.ForeignKey(DocumentType, verbose_name="Document Type", on_delete=models.CASCADE)
    datetime = models.DateTimeField("Datetime")
    data = models.CharField('Data', max_length=200)


# Nasdaq
class NasdaqODAPALUMUSD(models.Model):
    date = models.DateField("Date")
    value = models.FloatField()


class NasdaqODAPCOPPUSD(models.Model):
    date = models.DateField("Date")
    value = models.FloatField()


class NasdaqSHFERBV2013(models.Model):
    date = models.DateField("Date")
    pre_settle = models.FloatField(null=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    settle = models.FloatField(null=True)
    ch1 = models.FloatField(null=True)
    ch2 = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    prev = models.FloatField(null=True)
    change = models.FloatField(null=True)


class NasdaqODAPNICKUSD(models.Model):
    date = models.DateField("Date")
    value = models.FloatField(null=True)


class NasdaqJOHNMATTPLAT(models.Model):
    date = models.DateField("Date")
    hong_kong_8_30 = models.FloatField(null=True)
    hong_kong_14_00 = models.FloatField(null=True)
    london_09_00 = models.FloatField(null=True)
    new_york_9_30 = models.FloatField(null=True)


class NasdaqJOHNMATTPALL(models.Model):
    date = models.DateField("Date")
    hong_kong_8_30 = models.FloatField(null=True)
    hong_kong_14_00 = models.FloatField(null=True)
    london_09_00 = models.FloatField(null=True)
    new_york_9_30 = models.FloatField(null=True)
