from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum
from .models import Reed, UsageSession, QualitySnapshot, Modification, Thread, Staple
from .serializers import (
    ReedSerializer, ReedListSerializer, UsageSessionSerializer,
    QualitySnapshotSerializer, ModificationSerializer, ThreadSerializer, StapleSerializer
)


class ReedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reed model with analytics capabilities.
    """
    queryset = Reed.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReedListSerializer
        return ReedSerializer
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Provides analytical insights for a specific reed.
        """
        reed = self.get_object()
        
        # Calculate averages from quality snapshots
        quality_stats = reed.quality_snapshots.aggregate(
            avg_tone=Avg('tone_quality'),
            avg_response=Avg('response'),
            avg_intonation=Avg('intonation'),
            avg_stability=Avg('stability'),
            avg_ease=Avg('ease_of_playing'),
            avg_overall=Avg('overall_rating'),
            snapshot_count=Count('id')
        )
        
        # Usage statistics
        usage_stats = reed.usage_sessions.aggregate(
            total_sessions=Count('id'),
            total_minutes=Sum('duration_minutes')
        )
        
        # Modification statistics
        mod_stats = reed.modifications.aggregate(
            total_modifications=Count('id'),
            avg_success=Avg('success_rating')
        )
        
        # Get modification type breakdown
        mod_types = {}
        for mod in reed.modifications.values('modification_type').annotate(count=Count('id')):
            mod_types[mod['modification_type']] = mod['count']
        
        # Calculate age in days from creation to now
        from django.utils import timezone
        age_days = (timezone.now() - reed.created_date).days
        
        return Response({
            'reed_id': reed.id,
            'reed_name': reed.name,
            'status': reed.status,
            'age_days': age_days,
            'quality_metrics': quality_stats,
            'usage_metrics': usage_stats,
            'modification_metrics': {
                **mod_stats,
                'types_breakdown': mod_types
            }
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Provides overall summary analytics across all reeds.
        """
        total_reeds = Reed.objects.count()
        status_breakdown = {}
        for status_choice in Reed.STATUS_CHOICES:
            status_breakdown[status_choice[0]] = Reed.objects.filter(status=status_choice[0]).count()
        
        # Overall quality averages across all reeds
        all_quality_stats = QualitySnapshot.objects.aggregate(
            avg_tone=Avg('tone_quality'),
            avg_response=Avg('response'),
            avg_intonation=Avg('intonation'),
            avg_overall=Avg('overall_rating')
        )
        
        # Total usage across all reeds
        total_usage = Reed.objects.aggregate(
            total_play_time=Sum('total_play_time_minutes')
        )
        
        return Response({
            'total_reeds': total_reeds,
            'status_breakdown': status_breakdown,
            'overall_quality_metrics': all_quality_stats,
            'total_usage': total_usage
        })


class UsageSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UsageSession model.
    """
    queryset = UsageSession.objects.all()
    serializer_class = UsageSessionSerializer
    filterset_fields = ['reed', 'context']
    ordering_fields = ['start_time', 'duration_minutes']


class QualitySnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for QualitySnapshot model.
    """
    queryset = QualitySnapshot.objects.all()
    serializer_class = QualitySnapshotSerializer
    filterset_fields = ['reed']
    ordering_fields = ['timestamp', 'overall_rating']


class ModificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Modification model.
    """
    queryset = Modification.objects.all()
    serializer_class = ModificationSerializer
    filterset_fields = ['reed', 'modification_type']
    ordering_fields = ['timestamp', 'success_rating']


class ThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Thread model.
    """
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    filterset_fields = ['color']
    ordering_fields = ['color']


class StapleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staple model with bulk creation support.
    """
    queryset = Staple.objects.all()
    serializer_class = StapleSerializer
    filterset_fields = ['material', 'shape', 'make']
    ordering_fields = ['material', 'shape']
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple staples of the same type at once.
        Example: POST with material='brass', shape='recessed', make='Pisoni', 
                 length_mm=47, quantity=5
        """
        quantity = request.data.get('quantity', 1)
        
        if quantity < 1:
            return Response(
                {'error': 'Quantity must be at least 1'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a single staple with the specified quantity
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

