from rest_framework import serializers
from .models import Reed, UsageSession, QualitySnapshot, Modification, Thread, Staple


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'color', 'gauge']
        read_only_fields = ['id']


class StapleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staple
        fields = ['id', 'material', 'shape', 'make', 'length_mm', 'quantity']
        read_only_fields = ['id']


class ModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modification
        fields = ['id', 'reed', 'timestamp', 'modification_type', 'description', 'goal', 'success_rating']
        read_only_fields = ['id']


class QualitySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitySnapshot
        fields = [
            'id', 'reed', 'timestamp', 'tone_quality', 'response', 'intonation',
            'stability', 'ease_of_playing', 'overall_rating', 'notes'
        ]
        read_only_fields = ['id']


class UsageSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageSession
        fields = ['id', 'reed', 'start_time', 'end_time', 'duration_minutes', 'context', 'notes']
        read_only_fields = ['id', 'duration_minutes']


class ReedSerializer(serializers.ModelSerializer):
    usage_sessions = UsageSessionSerializer(many=True, read_only=True)
    quality_snapshots = QualitySnapshotSerializer(many=True, read_only=True)
    modifications = ModificationSerializer(many=True, read_only=True)
    thread_detail = ThreadSerializer(source='thread', read_only=True)
    staple_detail = StapleSerializer(source='staple', read_only=True)
    
    class Meta:
        model = Reed
        fields = [
            'id', 'name', 'thread', 'thread_detail', 'staple', 'staple_detail',
            'created_date', 'status', 'cane_source', 'shape',
            'gouge_thickness', 'notes', 'total_play_time_minutes',
            'usage_sessions', 'quality_snapshots', 'modifications'
        ]
        read_only_fields = ['id', 'total_play_time_minutes']


class ReedListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views without nested relationships"""
    thread_detail = ThreadSerializer(source='thread', read_only=True)
    staple_detail = StapleSerializer(source='staple', read_only=True)
    
    class Meta:
        model = Reed
        fields = [
            'id', 'name', 'thread', 'thread_detail', 'staple', 'staple_detail',
            'created_date', 'status', 'cane_source', 'shape',
            'gouge_thickness', 'total_play_time_minutes'
        ]
        read_only_fields = ['id', 'total_play_time_minutes']
