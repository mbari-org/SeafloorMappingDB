# Generated by Django 3.2.12 on 2022-03-19 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smdb', '0045_compilation_thumbnail_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mission',
            name='compilation',
        ),
    ]
