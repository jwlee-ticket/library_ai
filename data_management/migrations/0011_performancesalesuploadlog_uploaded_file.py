from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data_management', '0010_performancedailysalesgrade_occupancy_rates'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancesalesuploadlog',
            name='uploaded_file',
            field=models.FileField(
                blank=True,
                help_text='업로드된 엑셀 파일',
                null=True,
                upload_to='sales_uploads/',
                verbose_name='업로드 파일',
            ),
        ),
    ]
