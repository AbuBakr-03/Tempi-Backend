# TempiApp/models.py
from django.db import models
from django.contrib.auth.models import User


class CompanyProfile(models.Model):
    """Profile for companies, similar to UserProfile"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="company_profile"
    )
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} Profile"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class JobType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Job(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    pay = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(max_length=1000)
    qualifications = models.TextField(max_length=1000)
    responsibilities = models.TextField(max_length=1000)
    nice_to_haves = models.TextField(max_length=1000)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE, null=None)
    company = models.ForeignKey(
        User,
        related_name="company_jobs",
        on_delete=models.CASCADE,
        limit_choices_to={"groups__name": "Company"},
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=None)

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["location"]),
            models.Index(fields=["pay"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["company"]),
            models.Index(fields=["category"]),
        ]


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "job")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["job"]),
        ]


class Status(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    class Meta:
        unique_together = ("user", "job")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["job"]),
            models.Index(fields=["status"]),
        ]


class JobAssignmentStatus(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class JobAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    status = models.ForeignKey(JobAssignmentStatus, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "job")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["job"]),
        ]

    def __str__(self):
        return f"{self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    skill = models.TextField(max_length=500, blank=True, null=True)
    experience = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# No signals needed - profile creation is handled in the serializer
