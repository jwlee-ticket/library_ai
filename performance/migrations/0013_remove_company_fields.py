from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0012_alter_performance_company_alter_person_company'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='performance',
            name='performance_company_bca67b_idx',
        ),
        migrations.RemoveIndex(
            model_name='person',
            name='performance_company_c6996b_idx',
        ),
        migrations.RemoveField(
            model_name='performance',
            name='company',
        ),
        migrations.RemoveField(
            model_name='person',
            name='company',
        ),
    ]
