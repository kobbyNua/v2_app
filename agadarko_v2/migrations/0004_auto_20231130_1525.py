# Generated by Django 3.2.4 on 2023-11-30 15:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agadarko_v2', '0003_auto_20231124_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient_laboratory_test_records',
            name='amount_paid',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='patient_laboratory_test_records',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='patient_medical_history_records',
            name='time_checked_in',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 11, 30, 15, 25, 27, 368181)),
        ),
        migrations.AlterField(
            model_name='patient_medical_history_records',
            name='time_checked_out',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 30, 15, 25, 27, 368181)),
        ),
    ]