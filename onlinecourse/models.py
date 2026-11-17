from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_enrollment = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    content = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} (Course: {self.course.name})"


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=200, blank=True)
    social_link = models.URLField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Enrollment(models.Model):
    MODE_CHOICES = (
        ("audit", "Audit"),
        ("honor", "Honor"),
        ("beta", "Beta"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    mode = models.CharField(max_length=5, choices=MODE_CHOICES, default="audit")
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name}"

# Assessment models

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, null=True, blank=True)
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)  # points for this question

    def __str__(self):
        return self.content

    def is_get_score(self, selected_ids):
        """Return True if the selected choice IDs exactly match the set of correct choices.
        """
        correct_ids = set(self.choice_set.filter(is_correct=True).values_list('id', flat=True))
        selected_set = set(selected_ids)
        return correct_ids == selected_set


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.enrollment.user.username} for {self.enrollment.course.name}"