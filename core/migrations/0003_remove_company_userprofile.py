from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_assign_default_company'),
        ('performance', '0013_remove_company_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
    ]
