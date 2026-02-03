from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0014_make_performance_optional_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CastingRole',
        ),
        migrations.DeleteModel(
            name='CrewRole',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]
