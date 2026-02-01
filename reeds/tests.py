from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Reed, UsageSession, QualitySnapshot, Modification


class ReedModelTest(TestCase):
    """Test the Reed model"""
    
    def setUp(self):
        self.reed = Reed.objects.create(
            name="Test Reed #1",
            status="new",
            cane_source="Test Cane Co.",
            shape="Test Shape",
            gouge_thickness=0.58
        )
    
    def test_reed_creation(self):
        """Test that a reed is created successfully"""
        self.assertEqual(self.reed.name, "Test Reed #1")
        self.assertEqual(self.reed.status, "new")
        self.assertEqual(self.reed.total_play_time_minutes, 0)
    
    def test_reed_str_representation(self):
        """Test the string representation of Reed"""
        self.assertEqual(str(self.reed), "Test Reed #1 (new)")


class UsageSessionModelTest(TestCase):
    """Test the UsageSession model"""
    
    def setUp(self):
        self.reed = Reed.objects.create(name="Test Reed", status="prime")
    
    def test_usage_session_duration_calculation(self):
        """Test that duration is calculated correctly"""
        start = timezone.now()
        end = start + timedelta(minutes=45)
        
        session = UsageSession.objects.create(
            reed=self.reed,
            start_time=start,
            end_time=end,
            context="Practice"
        )
        
        self.assertEqual(session.duration_minutes, 45)
    
    def test_reed_total_play_time_update(self):
        """Test that reed's total play time is updated"""
        start = timezone.now()
        end = start + timedelta(minutes=30)
        
        UsageSession.objects.create(
            reed=self.reed,
            start_time=start,
            end_time=end
        )
        
        self.reed.refresh_from_db()
        self.assertEqual(self.reed.total_play_time_minutes, 30)


class QualitySnapshotModelTest(TestCase):
    """Test the QualitySnapshot model"""
    
    def setUp(self):
        self.reed = Reed.objects.create(name="Test Reed", status="prime")
    
    def test_quality_snapshot_creation(self):
        """Test creating a quality snapshot"""
        snapshot = QualitySnapshot.objects.create(
            reed=self.reed,
            tone_quality=8,
            response=7,
            intonation=9,
            stability=8,
            ease_of_playing=8,
            overall_rating=8
        )
        
        self.assertEqual(snapshot.tone_quality, 8)
        self.assertEqual(snapshot.overall_rating, 8)


class ModificationModelTest(TestCase):
    """Test the Modification model"""
    
    def setUp(self):
        self.reed = Reed.objects.create(name="Test Reed", status="prime")
    
    def test_modification_creation(self):
        """Test creating a modification"""
        mod = Modification.objects.create(
            reed=self.reed,
            modification_type="clip",
            description="Clipped 0.5mm",
            goal="Improve response",
            success_rating=8
        )
        
        self.assertEqual(mod.modification_type, "clip")
        self.assertEqual(mod.success_rating, 8)


class ReedAPITest(APITestCase):
    """Test the Reed API endpoints"""
    
    def setUp(self):
        self.reed = Reed.objects.create(
            name="API Test Reed",
            status="prime",
            cane_source="Test Cane"
        )
    
    def test_get_reeds_list(self):
        """Test getting list of reeds"""
        response = self.client.get('/api/reeds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_reed_detail(self):
        """Test getting a single reed"""
        response = self.client.get(f'/api/reeds/{self.reed.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "API Test Reed")
    
    def test_create_reed(self):
        """Test creating a new reed via API"""
        data = {
            'name': 'New API Reed',
            'status': 'new',
            'cane_source': 'Test Source'
        }
        response = self.client.post('/api/reeds/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reed.objects.count(), 2)
    
    def test_update_reed(self):
        """Test updating a reed"""
        data = {'status': 'declining'}
        response = self.client.patch(f'/api/reeds/{self.reed.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reed.refresh_from_db()
        self.assertEqual(self.reed.status, 'declining')
    
    def test_reed_analytics_endpoint(self):
        """Test the analytics endpoint for a reed"""
        # Add some data
        QualitySnapshot.objects.create(
            reed=self.reed,
            overall_rating=8,
            tone_quality=8
        )
        
        response = self.client.get(f'/api/reeds/{self.reed.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('quality_metrics', response.data)
        self.assertIn('usage_metrics', response.data)
    
    def test_summary_endpoint(self):
        """Test the summary endpoint"""
        response = self.client.get('/api/reeds/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reeds', response.data)
        self.assertEqual(response.data['total_reeds'], 1)


class UsageSessionAPITest(APITestCase):
    """Test the UsageSession API endpoints"""
    
    def setUp(self):
        self.reed = Reed.objects.create(name="Test Reed", status="prime")
    
    def test_create_usage_session(self):
        """Test creating a usage session via API"""
        data = {
            'reed': self.reed.id,
            'start_time': timezone.now().isoformat(),
            'context': 'Practice'
        }
        response = self.client.post('/api/usage-sessions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

