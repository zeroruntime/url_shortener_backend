# Generated migration for custom_alias field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='links',
            name='custom_alias',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True, unique=True),
        ),
    ]
