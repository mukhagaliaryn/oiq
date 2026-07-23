from django.db import migrations


def copy_subject_to_subjects(apps, schema_editor):
    Teacher = apps.get_model('accounts', 'Teacher')

    for teacher in Teacher.objects.exclude(subject__isnull=True):
        teacher.subjects.add(teacher.subject_id)


def copy_subjects_to_subject(apps, schema_editor):
    Teacher = apps.get_model('accounts', 'Teacher')

    for teacher in Teacher.objects.all():
        first_subject_id = teacher.subjects.values_list('id', flat=True).first()
        if first_subject_id:
            teacher.subject_id = first_subject_id
            teacher.save(update_fields=['subject'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_teacher_subjects_m2m'),
    ]

    operations = [
        migrations.RunPython(copy_subject_to_subjects, copy_subjects_to_subject),
    ]
