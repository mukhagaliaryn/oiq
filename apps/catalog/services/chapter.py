from apps.catalog.models import Chapter


def create_chapter(*, subject, grade=None, title, description='', order=0):
    return Chapter.objects.create(
        subject=subject, grade=grade, title=title, description=description, order=order,
    )


def update_chapter(chapter, **fields):
    for name, value in fields.items():
        setattr(chapter, name, value)
    chapter.save(update_fields=list(fields.keys()))
    return chapter


def delete_chapter(chapter):
    chapter.is_active = False
    chapter.save(update_fields=['is_active'])
    return chapter
