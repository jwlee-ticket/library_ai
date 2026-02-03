from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0005_concertdailysalesgrade_concertfinalsalesgrade_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ConcertDailySales',
            new_name='PerformanceDailySales',
        ),
        migrations.RenameModel(
            old_name='ConcertDailySalesGrade',
            new_name='PerformanceDailySalesGrade',
        ),
        migrations.RenameModel(
            old_name='ConcertFinalSales',
            new_name='PerformanceFinalSales',
        ),
        migrations.RenameModel(
            old_name='ConcertFinalSalesGrade',
            new_name='PerformanceFinalSalesGrade',
        ),
    ]
