# Generated by Django 3.2.11 on 2022-02-02 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smdb', '0039_auto_20220201_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='compilation',
            name='creation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
