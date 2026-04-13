from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("smdb", "0057_alter_mission_area"),
    ]

    operations = [
        migrations.AlterField(
            model_name="citation",
            name="full_reference",
            field=models.CharField(db_index=True, max_length=512),
        ),
    ]
