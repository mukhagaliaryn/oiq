def update_subject(subject, **fields):
    for name, value in fields.items():
        setattr(subject, name, value)
    subject.save(update_fields=list(fields.keys()))
    return subject


def remove_subject_cover(subject):
    if subject.cover:
        subject.cover.delete(save=False)
        subject.save(update_fields=['cover'])
    return subject
