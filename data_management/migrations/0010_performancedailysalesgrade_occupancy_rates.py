from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data_management', '0009_performancedailysales_upload_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancedailysalesgrade',
            name='paid_occupancy_rate',
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=5,
                null=True,
                help_text='Seat details의 유료 점유율',
                verbose_name='입금 점유율',
            ),
        ),
        migrations.AddField(
            model_name='performancedailysalesgrade',
            name='total_occupancy_rate',
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=5,
                null=True,
                help_text='Seat details의 객석 점유율',
                verbose_name='객석 점유율',
            ),
        ),
    ]
