from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role',
            new_name='account_type',
        ),
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('teacher', 'Teacher'),
                    ('learner', 'Learner'),
                    ('school_user', 'School system user'),
                ],
                default='learner',
                help_text='Shows which product the user belongs to (teaching/learning/school).',
                max_length=16,
                verbose_name='Account type',
            ),
        ),
    ]
