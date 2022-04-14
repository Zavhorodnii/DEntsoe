from django.db import models

# Create your models here.


class Country(models.Model):
    country = models.CharField('Country', max_length=100)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class Source(models.Model):
    country = models.ForeignKey(Country, verbose_name="Country", on_delete=models.CASCADE)
    source = models.CharField("Source", max_length=150)

    def __str__(self):
        return self.source


class Data(models.Model):
    source = models.ForeignKey(Source, verbose_name="Source", on_delete=models.CASCADE)
    datetime = models.DateTimeField("Datetime")
    data = models.CharField('Data', max_length=200)
