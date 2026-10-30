
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('plant_catalog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plantreview',
            name='plant',
        ),
        migrations.AddField(
            model_name='plantreview',
            name='plant',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reviews',
                to='plant_catalog.plant',
            ),
        ),
        migrations.DeleteModel(
            name='Plant',
        ),
    ]

