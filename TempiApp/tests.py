from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from .models import (
    JobAssignmentStatus, 
    Job, 
    Application, 
    Status, 
    JobAssignment, 
    Rating,
    Category,
    JobType,
    CompanyProfile,
    UserProfile
)

# Create your tests here.

class RatingRestrictionTest(APITestCase):
    def setUp(self):
        # Create status objects
        self.pending_status = JobAssignmentStatus.objects.create(name="Pending Start")
        self.in_progress_status = JobAssignmentStatus.objects.create(name="In Progress")
        self.completed_status = JobAssignmentStatus.objects.create(name="Completed")
        self.cancelled_status = JobAssignmentStatus.objects.create(name="Cancelled")
        
        # Create application status
        self.applied_status = Status.objects.create(name="Applied")
        self.approved_status = Status.objects.create(name="Approved")
        self.rejected_status = Status.objects.create(name="Rejected")
        self.shortlisted_status = Status.objects.create(name="Shortlisted")
        
        # Create groups
        self.company_group = Group.objects.create(name="Company")
        self.user_group = Group.objects.create(name="User")
        
        # Create users
        self.company_user = User.objects.create_user(
            username="company1", 
            email="company1@test.com", 
            password="testpass123"
        )
        self.company_user.groups.add(self.company_group)
        
        self.worker_user = User.objects.create_user(
            username="worker1", 
            email="worker1@test.com", 
            password="testpass123"
        )
        self.worker_user.groups.add(self.user_group)
        
        self.other_user = User.objects.create_user(
            username="other1", 
            email="other1@test.com", 
            password="testpass123"
        )
        self.other_user.groups.add(self.user_group)
        
        # Create company profile
        self.company_profile = CompanyProfile.objects.create(
            user=self.company_user,
            name="Test Company",
            industry="Technology"
        )
        
        # Create job categories and types
        self.category = Category.objects.create(name="Technology")
        self.job_type = JobType.objects.create(name="Full-time")
        
        # Create a job
        self.job = Job.objects.create(
            title="Test Job",
            location="Remote",
            pay=50.00,
            description="Test job description",
            qualifications="Test qualifications",
            responsibilities="Test responsibilities",
            nice_to_haves="Test nice to haves",
            start_date="2024-01-01",
            end_date="2024-12-31",
            start_time="09:00:00",
            end_time="17:00:00",
            category=self.category,
            company=self.company_user,
            job_type=self.job_type
        )
        
        # Create an application
        self.application = Application.objects.create(
            name="Test Worker",
            email="worker1@test.com",
            phone_number="1234567890",
            location="Remote",
            user=self.worker_user,
            job=self.job,
            status=self.applied_status
        )

    def test_cannot_rate_without_completed_task(self):
        """Test that users cannot rate each other without completing a task together"""
        self.client.force_authenticate(user=self.worker_user)
        
        # Try to rate the company without any completed task
        response = self.client.post('/api/ratings/', {
            'rated_user_id': self.company_user.id,
            'rating': 5,
            'comment': 'Great company!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating restriction', response.data['error'])

    def test_can_rate_after_completed_task(self):
        """Test that users can rate each other after completing a task together"""
        # Create a completed job assignment
        completed_assignment = JobAssignment.objects.create(
            user=self.worker_user,
            job=self.job,
            application=self.application,
            status=self.completed_status
        )
        
        self.client.force_authenticate(user=self.worker_user)
        
        # Now try to rate the company after completing a task
        response = self.client.post('/api/ratings/', {
            'rated_user_id': self.company_user.id,
            'rating': 5,
            'comment': 'Great company!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the rating was created
        rating = Rating.objects.first()
        self.assertEqual(rating.rater, self.worker_user)
        self.assertEqual(rating.rated_user, self.company_user)
        self.assertEqual(rating.rating, 5)

    def test_company_can_rate_worker_after_completed_task(self):
        """Test that companies can rate workers after completing a task together"""
        # Create a completed job assignment
        completed_assignment = JobAssignment.objects.create(
            user=self.worker_user,
            job=self.job,
            application=self.application,
            status=self.completed_status
        )
        
        self.client.force_authenticate(user=self.company_user)
        
        # Company rates the worker
        response = self.client.post('/api/ratings/', {
            'rated_user_id': self.worker_user.id,
            'rating': 4,
            'comment': 'Great worker!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the rating was created
        rating = Rating.objects.first()
        self.assertEqual(rating.rater, self.company_user)
        self.assertEqual(rating.rated_user, self.worker_user)
        self.assertEqual(rating.rating, 4)

    def test_cannot_rate_self(self):
        """Test that users cannot rate themselves"""
        self.client.force_authenticate(user=self.worker_user)
        
        response = self.client.post('/api/ratings/', {
            'rated_user_id': self.worker_user.id,
            'rating': 5,
            'comment': 'Great job!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot rate yourself', str(response.data))


class ShortlistTest(APITestCase):
    def setUp(self):
        # Get or create status objects with specific IDs to match the system
        self.pending_status, _ = Status.objects.get_or_create(id=1, defaults={'name': "Pending"})
        self.approved_status, _ = Status.objects.get_or_create(id=2, defaults={'name': "Approved"})
        self.rejected_status, _ = Status.objects.get_or_create(id=3, defaults={'name': "Rejected"})
        self.shortlisted_status, _ = Status.objects.get_or_create(id=4, defaults={'name': "Shortlisted"})
        
        # Create JobAssignmentStatus objects
        self.job_assignment_status, _ = JobAssignmentStatus.objects.get_or_create(
            id=1, 
            defaults={'name': "Active"}
        )
        
        # Create groups
        self.company_group = Group.objects.create(name="Company")
        self.user_group = Group.objects.create(name="User")
        
        # Create users
        self.company_user = User.objects.create_user(
            username="company1", 
            email="company1@test.com", 
            password="testpass123"
        )
        self.company_user.groups.add(self.company_group)
        
        self.worker1 = User.objects.create_user(
            username="worker1", 
            email="worker1@test.com", 
            password="testpass123"
        )
        self.worker1.groups.add(self.user_group)
        
        self.worker2 = User.objects.create_user(
            username="worker2", 
            email="worker2@test.com", 
            password="testpass123"
        )
        self.worker2.groups.add(self.user_group)
        
        # Create company profile
        self.company_profile = CompanyProfile.objects.create(
            user=self.company_user,
            name="Test Company",
            industry="Technology"
        )
        
        # Create job categories and types
        self.category = Category.objects.create(name="Technology")
        self.job_type = JobType.objects.create(name="Full-time")
        
        # Create a job
        self.job = Job.objects.create(
            title="Test Job",
            location="Remote",
            pay=50.00,
            description="Test job description",
            qualifications="Test qualifications",
            responsibilities="Test responsibilities",
            nice_to_haves="Test nice to haves",
            start_date="2024-01-01",
            end_date="2024-12-31",
            start_time="09:00:00",
            end_time="17:00:00",
            category=self.category,
            company=self.company_user,
            job_type=self.job_type
        )
        
        # Create applications
        self.application1 = Application.objects.create(
            name="Test Worker 1",
            email="worker1@test.com",
            phone_number="1234567890",
            location="Remote",
            user=self.worker1,
            job=self.job,
            status=self.pending_status
        )
        
        self.application2 = Application.objects.create(
            name="Test Worker 2",
            email="worker2@test.com",
            phone_number="0987654321",
            location="Remote",
            user=self.worker2,
            job=self.job,
            status=self.pending_status
        )

    def test_company_can_shortlist_applicant(self):
        """Test that company can shortlist an applicant"""
        self.client.force_authenticate(user=self.company_user)
        
        # Shortlist the first applicant
        response = self.client.patch(f'/api/application/{self.application1.id}/', {
            'status_id': self.shortlisted_status.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.application1.refresh_from_db()
        self.assertEqual(self.application1.status, self.shortlisted_status)

    def test_company_can_shortlist_multiple_applicants(self):
        """Test that company can shortlist multiple applicants"""
        self.client.force_authenticate(user=self.company_user)
        
        # Shortlist both applicants
        response1 = self.client.patch(f'/api/application/{self.application1.id}/', {
            'status_id': self.shortlisted_status.id
        })
        response2 = self.client.patch(f'/api/application/{self.application2.id}/', {
            'status_id': self.shortlisted_status.id
        })
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.application1.refresh_from_db()
        self.application2.refresh_from_db()
        self.assertEqual(self.application1.status, self.shortlisted_status)
        self.assertEqual(self.application2.status, self.shortlisted_status)

    def test_approving_applicant_rejects_all_others_including_shortlisted(self):
        """Test that approving an applicant rejects all others including shortlisted ones"""
        self.client.force_authenticate(user=self.company_user)
        
        # First shortlist both applicants
        self.client.patch(f'/api/application/{self.application1.id}/', {
            'status': self.shortlisted_status.id
        })
        self.client.patch(f'/api/application/{self.application2.id}/', {
            'status': self.shortlisted_status.id
        })
        
        # Now approve the first applicant
        response = self.client.patch(f'/api/application/{self.application1.id}/', {
            'status_id': self.approved_status.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.application1.refresh_from_db()
        self.application2.refresh_from_db()
        
        # First applicant should be approved
        self.assertEqual(self.application1.status, self.approved_status)
        # Second applicant should be rejected (even though it was shortlisted)
        self.assertEqual(self.application2.status, self.rejected_status)

    def test_approving_shortlisted_applicant_creates_job_assignment(self):
        """Test that approving a shortlisted applicant creates a job assignment"""
        self.client.force_authenticate(user=self.company_user)
        
        # Shortlist the applicant
        self.client.patch(f'/api/application/{self.application1.id}/', {
            'status_id': self.shortlisted_status.id
        })
        
        # Now approve the shortlisted applicant
        response = self.client.patch(f'/api/application/{self.application1.id}/', {
            'status_id': self.approved_status.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that a job assignment was created
        job_assignment = JobAssignment.objects.filter(
            user=self.worker1,
            job=self.job,
            application=self.application1
        ).first()
        
        self.assertIsNotNone(job_assignment)


class BadgeTest(APITestCase):
    def setUp(self):
        # Create groups
        self.company_group = Group.objects.create(name="Company")
        self.user_group = Group.objects.create(name="User")
        
        # Create users
        self.company_user = User.objects.create_user(
            username="company1", 
            email="company1@test.com", 
            password="testpass123"
        )
        self.company_user.groups.add(self.company_group)
        
        self.worker1 = User.objects.create_user(
            username="worker1", 
            email="worker1@test.com", 
            password="testpass123"
        )
        self.worker1.groups.add(self.user_group)
        
        self.worker2 = User.objects.create_user(
            username="worker2", 
            email="worker2@test.com", 
            password="testpass123"
        )
        self.worker2.groups.add(self.user_group)
        
        # Create profiles
        self.user_profile1 = UserProfile.objects.create(user=self.worker1)
        self.user_profile2 = UserProfile.objects.create(user=self.worker2)
        self.company_profile = CompanyProfile.objects.create(
            user=self.company_user,
            name="Test Company",
            industry="Technology"
        )
        
        # Create additional users to act as raters
        self.rater1 = User.objects.create_user(
            username="rater1", 
            email="rater1@test.com", 
            password="testpass123"
        )
        self.rater1.groups.add(self.user_group)
        
        self.rater2 = User.objects.create_user(
            username="rater2", 
            email="rater2@test.com", 
            password="testpass123"
        )
        self.rater2.groups.add(self.user_group)
        
        # Create ratings to test badges
        # Worker1 gets high ratings (4.5+ average) from different raters
        Rating.objects.create(
            rater=self.company_user,
            rated_user=self.worker1,
            rating=5
        )
        Rating.objects.create(
            rater=self.rater1,
            rated_user=self.worker1,
            rating=4
        )
        
        # Worker2 gets lower ratings (below 4.5 average) from different raters
        Rating.objects.create(
            rater=self.company_user,
            rated_user=self.worker2,
            rating=3
        )
        Rating.objects.create(
            rater=self.rater1,
            rated_user=self.worker2,
            rating=4
        )
        
        # Company gets high ratings (4.5+ average) from different raters
        Rating.objects.create(
            rater=self.worker1,
            rated_user=self.company_user,
            rating=5
        )
        Rating.objects.create(
            rater=self.rater2,
            rated_user=self.company_user,
            rating=4
        )

    def test_badge_automatically_assigned(self):
        """Test that badges are automatically assigned when rating threshold is met"""
        # Check that worker1 has the badge (4.5 average)
        self.user_profile1.refresh_from_db()
        self.assertTrue(self.user_profile1.has_best_tempi_badge)
        self.assertIsNotNone(self.user_profile1.badge_earned_date)
        
        # Check that worker2 doesn't have the badge (3.5 average)
        self.user_profile2.refresh_from_db()
        self.assertFalse(self.user_profile2.has_best_tempi_badge)
        self.assertIsNone(self.user_profile2.badge_earned_date)
        
        # Check that company has the badge (4.5 average)
        self.company_profile.refresh_from_db()
        self.assertTrue(self.company_profile.has_best_employer_badge)
        self.assertIsNotNone(self.company_profile.badge_earned_date)
