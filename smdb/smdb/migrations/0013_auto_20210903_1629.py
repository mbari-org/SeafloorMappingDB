# Generated by Django 3.2.6 on 2021-09-03 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smdb', '0012_rename_sensor_type_name_sensortype_sensortype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='kml_filename',
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='mission',
            name='notes_filename',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='region_name',
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='mission',
            name='site_detail',
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='mission',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='thumbnail_filename',
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
    ]
