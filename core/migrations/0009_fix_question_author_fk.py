from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_question_author'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_question
                DROP CONSTRAINT IF EXISTS "core_question_author_id_29fa10ec_fk_core_user_id";

                ALTER TABLE core_question
                ADD CONSTRAINT "core_question_author_id_fk_core_teacher_id"
                FOREIGN KEY (author_id) REFERENCES core_teacher(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE core_question
                DROP CONSTRAINT IF EXISTS "core_question_author_id_fk_core_teacher_id";
            """,
        ),
    ]
