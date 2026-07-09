from apps.catalog.models import Topic


def create_topic(*, chapter, title, description='', order=0):
    return Topic.objects.create(
        chapter=chapter, title=title, description=description, order=order,
    )


def update_topic(topic, **fields):
    for name, value in fields.items():
        setattr(topic, name, value)
    topic.save(update_fields=list(fields.keys()))
    return topic


def delete_topic(topic):
    topic.is_active = False
    topic.save(update_fields=['is_active'])
    return topic
