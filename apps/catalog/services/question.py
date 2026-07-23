from apps.catalog.models import MatchPair, Option, Question


def create_question(*, topic, author, text, format, variant=None, level=Question.Level.EASY,
                     time_limit=30, options=None, match_pairs=None):
    question = Question.objects.create(
        topic=topic, author=author, text=text, format=format, variant=variant,
        level=level, time_limit=time_limit,
    )

    if options:
        Option.objects.bulk_create([
            Option(question=question, answer=option['answer'], is_correct=option.get('is_correct', False))
            for option in options
        ])

    if match_pairs:
        MatchPair.objects.bulk_create([
            MatchPair(question=question, left=pair['left'], right=pair['right'], order=index)
            for index, pair in enumerate(match_pairs)
        ])

    return question


def update_question(question, **fields):
    for name, value in fields.items():
        setattr(question, name, value)
    question.save(update_fields=list(fields.keys()))
    return question


def deactivate_question(question):
    question.is_active = False
    question.save(update_fields=['is_active'])
    return question
