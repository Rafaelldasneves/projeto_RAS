import django.db.models.deletion
from django.db import migrations, models


def copy_old_periods_to_new_periods(apps, schema_editor):
    ServiceOldPeriod = apps.get_model('service', 'Period')
    NewPeriod = apps.get_model('period', 'Period')
    Service = apps.get_model('service', 'Service')

    old_to_new = {}
    for old_period in ServiceOldPeriod.objects.all():
        new_period = NewPeriod.objects.create(
            name=old_period.name,
            date_start=old_period.date_start,
            date_end=old_period.date_end,
            description=old_period.description,
            date_at=old_period.date_at,
            updated_at=old_period.updated_at,
        )
        old_to_new[old_period.pk] = new_period.pk

    for service in Service.objects.all():
        if service.period_id in old_to_new:
            service.period_id = old_to_new[service.period_id]
            service.save(update_fields=['period_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('period', '0001_initial'),
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_old_periods_to_new_periods, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='service',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plantoes', to='period.period'),
        ),
        migrations.DeleteModel(
            name='Period',
        ),
    ]
