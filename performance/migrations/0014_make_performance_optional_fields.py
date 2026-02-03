from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0013_remove_company_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performance',
            name='venue',
            field=models.CharField(blank=True, max_length=200, verbose_name='공연장'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='address',
            field=models.CharField(blank=True, max_length=200, verbose_name='공연장 주소'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='performance_end',
            field=models.DateField(blank=True, null=True, verbose_name='공연 종료일'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='sales_start',
            field=models.DateField(blank=True, null=True, verbose_name='판매 시작일'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='sales_end',
            field=models.DateField(blank=True, null=True, verbose_name='판매 종료일'),
        ),
    ]
