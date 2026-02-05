from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0011_performancesalesuploadlog_uploaded_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceSalesUploadActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor_name', models.CharField(blank=True, max_length=150, verbose_name='사용자 이름')),
                ('original_filename', models.CharField(blank=True, max_length=255, verbose_name='파일명')),
                ('action_type', models.CharField(choices=[('upload', '업로드'), ('delete', '삭제'), ('download', '다운로드')], max_length=20, verbose_name='액션')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_upload_action_logs', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
                ('performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_upload_action_logs', to='performance.performance', verbose_name='공연')),
                ('upload_log', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_logs', to='data_management.performancesalesuploadlog', verbose_name='업로드 기록')),
            ],
            options={
                'verbose_name': '공연 매출 업로드 액션 이력',
                'verbose_name_plural': '공연 매출 업로드 액션 이력',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='performancesalesuploadactionlog',
            index=models.Index(fields=['performance', 'created_at'], name='data_manage_perform_2fd4b0_idx'),
        ),
        migrations.AddIndex(
            model_name='performancesalesuploadactionlog',
            index=models.Index(fields=['action_type'], name='data_manage_action__2c8395_idx'),
        ),
    ]
