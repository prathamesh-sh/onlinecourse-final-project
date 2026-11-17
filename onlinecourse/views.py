from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Course, Lesson, Enrollment, Question, Choice, Submission
from django.contrib.auth.decorators import login_required

# Course detail view (existing)
def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    lessons = course.lesson_set.all()
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course, 'lessons': lessons})

@login_required
def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if not enrollment:
        enrollment = Enrollment.objects.create(user=user, course=course, mode='audit')
    submission = Submission.objects.create(enrollment=enrollment)
    selected_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            try:
                selected_ids.append(int(value))
            except ValueError:
                continue
    choices = Choice.objects.filter(id__in=selected_ids)
    submission.choices.set(choices)
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)
    total_score = 0
    possible_score = 0
    for question in course.question_set.all():
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
    grade = round((total_score / possible_score) * 100) if possible_score else 0
    context = {'course': course, 'grade': grade, 'selected_choices': submission.choices.all()}
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
