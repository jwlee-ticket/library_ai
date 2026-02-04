from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0008_performancesalesuploadlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancedailysales',
            name='upload_log',
            field=models.ForeignKey(
                blank=True,
                help_text='엑셀 업로드 로그',
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='daily_sales',
                to='data_management.performancesalesuploadlog',
                verbose_name='업로드 기록',
            ),
        ),
    ]
