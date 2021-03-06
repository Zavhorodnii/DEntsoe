# Generated by Django 4.0.3 on 2022-04-23 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=100, verbose_name='Areas')),
            ],
        ),
        migrations.CreateModel(
            name='PsrType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('psrType', models.CharField(max_length=150, verbose_name='Source')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='getJsonData.area', verbose_name='Areas')),
            ],
        ),
        migrations.CreateModel(
            name='ProcessType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_type', models.CharField(max_length=150, verbose_name='process type')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='getJsonData.area', verbose_name='Area')),
            ],
        ),
        migrations.CreateModel(
            name='DayAheadData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='Datetime')),
                ('data', models.CharField(max_length=200, verbose_name='Data')),
                ('process_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='getJsonData.processtype', verbose_name='process type')),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='Datetime')),
                ('data', models.CharField(max_length=200, verbose_name='Data')),
                ('psrType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='getJsonData.psrtype', verbose_name='Source')),
            ],
        ),
    ]
