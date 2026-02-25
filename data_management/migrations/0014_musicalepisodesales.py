from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0013_rename_data_manage_perform_2fd4b0_idx_data_manage_perform_f51d47_idx_and_more'),
        ('performance', '0015_remove_artist_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicalEpisodeSales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('episode_no', models.IntegerField(validators=[MinValueValidator(1)], verbose_name='회차 No.')),
                ('show_date', models.DateField(verbose_name='공연일')),
                ('show_day', models.CharField(blank=True, max_length=10, verbose_name='요일')),
                ('show_time', models.TimeField(blank=True, null=True, verbose_name='공연 시간')),
                ('cast_map', models.JSONField(blank=True, default=dict, verbose_name='CAST')),
                ('paid_ticket_count', models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='유료 계(입금) 수량')),
                ('paid_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True, verbose_name='유료 계(입금) 비율')),
                ('paid_revenue', models.DecimalField(decimal_places=0, default=0, max_digits=14, validators=[MinValueValidator(0)], verbose_name='유료 계(입금) 금액')),
                ('unpaid_ticket_count', models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='유료 계(미입금) 수량')),
                ('unpaid_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True, verbose_name='유료 계(미입금) 비율')),
                ('unpaid_revenue', models.DecimalField(decimal_places=0, default=0, max_digits=14, validators=[MinValueValidator(0)], verbose_name='유료 계(미입금) 금액')),
                ('invited_ticket_count', models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='초대 수량')),
                ('invited_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True, verbose_name='초대 비율')),
                ('total_paid_ticket_count', models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='합계(입금) 수량')),
                ('total_paid_rate', models.DecimalField(blank=True, decimal_places=6, max_digits=7, null=True, verbose_name='합계(입금) 비율')),
                ('remark', models.TextField(blank=True, verbose_name='비고')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='musical_episode_sales', to='performance.performance', verbose_name='공연')),
                ('upload_log', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='musical_episode_sales', to='data_management.performancesalesuploadlog', verbose_name='업로드 기록')),
            ],
            options={
                'verbose_name': '뮤지컬 회차별 판매',
                'verbose_name_plural': '뮤지컬 회차별 판매',
                'ordering': ['performance', 'episode_no'],
                'indexes': [
                    models.Index(fields=['performance', 'show_date'], name='data_manage_perform_34f568_idx'),
                    models.Index(fields=['performance', 'show_date', 'show_time'], name='data_manage_perform_734cb0_idx'),
                    models.Index(fields=['upload_log'], name='data_manage_upload__5783a3_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('performance', 'episode_no'), name='uniq_musical_episode_no_performance'),
                ],
            },
        ),
    ]
