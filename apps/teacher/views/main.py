from django.db.models import Prefetch, Q
from django.shortcuts import render, get_object_or_404
from core.utils.decorators import role_required
from core.generics.models import Class, Letter, Teacher, Learner
from core.schools.models import SchoolClass, ClassSubject


# teacher dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_dashboard_view(request):
    teacher = request.user.teacher
    school = teacher.school
    classes = (
        SchoolClass.objects.filter(class_subjects__teachers=teacher, school=school)
        .select_related('grade', 'letter', 'school')
        .prefetch_related(
            Prefetch(
                'class_subjects',
                queryset=ClassSubject.objects.filter(teachers=teacher).select_related('subject'),
                to_attr='teacher_class_subjects',
            )
        )
        .distinct()[:5]
    )
    context = {
        'teacher': teacher,
        'classes': classes
    }
    return render(request, 'app/dashboard/teacher/page.html', context)


# teacher classes page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_classes_view(request):
    teacher = request.user.teacher

    teacher_classes = (
        SchoolClass.objects.filter(class_subjects__teachers=teacher)
        .select_related('grade', 'letter', 'school')
        .prefetch_related(
            Prefetch(
                'class_subjects',
                queryset=ClassSubject.objects.filter(teachers=teacher).select_related('subject'),
                to_attr='teacher_class_subjects',
            )
        )
        .distinct()
    )

    grade_id = request.GET.get('grade')
    letter_id = request.GET.get('letter')

    school_classes_qs = (
        SchoolClass.objects
        .filter(school=teacher.school)
        .exclude(class_subjects__teachers=teacher)
        .select_related('grade', 'letter', 'school')
    )
    if grade_id:
        school_classes_qs = school_classes_qs.filter(grade_id=grade_id)
    if letter_id:
        school_classes_qs = school_classes_qs.filter(letter_id=letter_id)

    school_classes = school_classes_qs.order_by('grade__id', 'letter__id')
    context = {
        'teacher': teacher,
        'teacher_classes': teacher_classes,
        'school_classes': school_classes,
        'selected_grade': grade_id,
        'selected_letter': letter_id,
        'grades': Class.objects.all(),
        'letters': Letter.objects.all(),
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'app/dashboard/teacher/classes/_school_classes_list.html', context)

    return render(request, 'app/dashboard/teacher/classes/page.html', context)


# teacher class page
@role_required('teacher')
def teacher_class_view(request, pk):
    teacher = request.user.teacher
    school_class = get_object_or_404(
        SchoolClass.objects.select_related('grade', 'letter', 'school'),
        pk=pk,
        school=teacher.school,
    )
    class_teachers = (
        Teacher.objects
        .filter(teaching_subjects__school_class=school_class)
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'teaching_subjects',
                queryset=ClassSubject.objects
                .filter(school_class=school_class)
                .select_related('subject'),
                to_attr='class_subjects_for_this_class',
            )
        )
        .distinct()
        .order_by('user__first_name', 'user__last_name')
    )

    learner_search = request.GET.get('learner_search')
    class_learners = (
        Learner.objects.filter(school_class=school_class)
        .select_related('user', 'school', 'school_class')
    )
    if learner_search:
        class_learners = class_learners.filter(
            Q(user__first_name=learner_search) | Q(user__last_name=learner_search) |
            Q(user__email=learner_search) | Q(user__username=learner_search)
        )

    context = {
        'teacher': teacher,
        'school_class': school_class,
        'class_teachers': class_teachers,
        'class_learners': class_learners,
    }
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'app/dashboard/teacher/classes/class/_class_learners_list.html', context)

    return render(request, 'app/dashboard/teacher/classes/class/page.html', context)


# teacher pupils page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def teacher_pupils_view(request):
    return render(request, 'app/dashboard/teacher/pupils/page.html', {})
