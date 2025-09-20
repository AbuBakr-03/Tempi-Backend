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
    has_best_employer_badge = models.BooleanField(default=False)
    badge_earned_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} Profile"
    
    def update_badge_status(self):
        """Update badge status based on average rating"""
        from django.utils import timezone
        
        ratings = self.user.received_ratings.all()
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            if avg_rating >= 4.5 and not self.has_best_employer_badge:
                self.has_best_employer_badge = True
                self.badge_earned_date = timezone.now()
                self.save()
            elif avg_rating < 4.5 and self.has_best_employer_badge:
                self.has_best_employer_badge = False
                self.badge_earned_date = None
                self.save()


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

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"

    def is_pending(self):
        """Check if application is pending"""
        return self.status.id == 1

    def is_shortlisted(self):
        """Check if application is shortlisted"""
        return self.status.id == 4

    def is_approved(self):
        """Check if application is approved"""
        return self.status.id == 2

    def is_rejected(self):
        """Check if application is rejected"""
        return self.status.id == 3

    def can_be_shortlisted(self):
        """Check if application can be shortlisted (must be pending)"""
        return self.is_pending()

    def can_be_approved(self):
        """Check if application can be approved (must be pending or shortlisted)"""
        return self.is_pending() or self.is_shortlisted()

    def can_be_rejected(self):
        """Check if application can be rejected (must be pending or shortlisted)"""
        return self.is_pending() or self.is_shortlisted()


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


# Add this simple model to TempiApp/models.py

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Rating(models.Model):
    """Simple rating system - users rate companies, companies rate users"""

    # Who is giving the rating
    rater = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_ratings"
    )

    # Who is being rated
    rated_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_ratings"
    )

    # Rating value (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Optional comment
    comment = models.TextField(max_length=500, blank=True, null=True)

    # When rating was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One rating per rater-rated_user pair
        unique_together = ("rater", "rated_user")

    def __str__(self):
        return (
            f"{self.rater.username} rated {self.rated_user.username}: {self.rating}/5"
        )

    def get_rater_type(self):
        return (
            "company" if self.rater.groups.filter(name="Company").exists() else "user"
        )

    def get_rated_user_type(self):
        return (
            "company"
            if self.rated_user.groups.filter(name="Company").exists()
            else "user"
        )

    @classmethod
    def can_rate_each_other(cls, user1, user2):
        """
        Check if two users can rate each other based on completed job assignments.
        Returns True if they have completed a task together.
        """
        from django.db.models import Q
        
        # Look for completed assignments where:
        # 1. One user is the worker and the other is the company
        # 2. Status is "Completed" (status_id = 3)
        completed_assignments = JobAssignment.objects.filter(
            Q(user=user1, job__company=user2) |  # User1 worked for User2's company
            Q(user=user2, job__company=user1),   # User2 worked for User1's company
            status_id=3  # Completed status
        )
        
        return completed_assignments.exists()


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
    has_best_tempi_badge = models.BooleanField(default=False)
    badge_earned_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_badge_status(self):
        """Update badge status based on average rating"""
        from django.utils import timezone
        
        ratings = self.user.received_ratings.all()
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            if avg_rating >= 4.5 and not self.has_best_tempi_badge:
                self.has_best_tempi_badge = True
                self.badge_earned_date = timezone.now()
                self.save()
            elif avg_rating < 4.5 and self.has_best_tempi_badge:
                self.has_best_tempi_badge = False
                self.badge_earned_date = None
                self.save()


# Signal handlers for automatic badge updates
@receiver([post_save, post_delete], sender=Rating)
def update_badge_on_rating_change(sender, instance, **kwargs):
    """Update badge status when a rating is created, updated, or deleted"""
    rated_user = instance.rated_user
    
    # Update user profile badge if user has a profile
    if hasattr(rated_user, 'profile'):
        rated_user.profile.update_badge_status()
    
    # Update company profile badge if user is a company
    if hasattr(rated_user, 'company_profile'):
        rated_user.company_profile.update_badge_status()