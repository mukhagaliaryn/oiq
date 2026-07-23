from django.db import migrations


def create_matching_format(apps, schema_editor):
    QuestionFormat = apps.get_model('catalog', 'QuestionFormat')
    QuestionFormat.objects.get_or_create(
        code='matching',
        defaults={'name': 'Сәйкестендіру', 'order': 2},
    )


def remove_matching_format(apps, schema_editor):
    QuestionFormat = apps.get_model('catalog', 'QuestionFormat')
    QuestionFormat.objects.filter(code='matching').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_add_match_pair'),
    ]

    operations = [
        migrations.RunPython(create_matching_format, remove_matching_format),
    ]
