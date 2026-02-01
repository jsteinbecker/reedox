from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Reed(models.Model):
    """
    Represents an oboe reed with its basic information.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('breaking_in', 'Breaking In'),
        ('prime', 'Prime'),
        ('declining', 'Declining'),
        ('retired', 'Retired'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name or identifier for this reed")
    created_date = models.DateTimeField(default=timezone.now, help_text="When the reed was created/started")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Reed construction details
    cane_source = models.CharField(max_length=200, blank=True, help_text="Source or brand of cane")
    shape = models.CharField(max_length=100, blank=True, help_text="Shape used for this reed")
    gouge_thickness = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Gouge thickness in mm"
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text="General notes about this reed")
    
    # Tracking
    total_play_time_minutes = models.IntegerField(
        default=0, help_text="Total time played with this reed in minutes"
    )
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class UsageSession(models.Model):
    """
    Tracks a session where a reed was used.
    """
    reed = models.ForeignKey(Reed, on_delete=models.CASCADE, related_name='usage_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(
        null=True, blank=True, help_text="Duration in minutes (calculated from start/end time)"
    )
    
    # Context of usage
    context = models.CharField(
        max_length=100, blank=True,
        help_text="e.g., 'Practice', 'Rehearsal', 'Performance', 'Lesson'"
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def save(self, *args, **kwargs):
        # Calculate duration if both start and end times are set
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            
            # Update total play time on the reed
            if self.pk:  # If updating existing session
                old_session = UsageSession.objects.get(pk=self.pk)
                old_duration = old_session.duration_minutes or 0
                self.reed.total_play_time_minutes -= old_duration
            
            self.reed.total_play_time_minutes += self.duration_minutes
            self.reed.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reed.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class QualitySnapshot(models.Model):
    """
    A snapshot of the reed's playing qualities at a specific point in time.
    """
    reed = models.ForeignKey(Reed, on_delete=models.CASCADE, related_name='quality_snapshots')
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Playing quality ratings (1-10 scale)
    tone_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Tone quality rating (1-10)"
    )
    response = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Response/articulation rating (1-10)"
    )
    intonation = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Intonation quality rating (1-10)"
    )
    stability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Stability/consistency rating (1-10)"
    )
    ease_of_playing = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Overall ease of playing (1-10)"
    )
    
    # Overall assessment
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Overall rating (1-10)"
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.reed.name} - Quality Snapshot {self.timestamp.strftime('%Y-%m-%d')}"


class Modification(models.Model):
    """
    Tracks modifications made to a reed.
    """
    MODIFICATION_TYPES = [
        ('clip', 'Clip'),
        ('scrape_tip', 'Scrape Tip'),
        ('scrape_heart', 'Scrape Heart'),
        ('scrape_back', 'Scrape Back'),
        ('scrape_rails', 'Scrape Rails'),
        ('adjust_wire', 'Adjust Wire'),
        ('trim_corners', 'Trim Corners'),
        ('balance', 'Balance'),
        ('other', 'Other'),
    ]
    
    reed = models.ForeignKey(Reed, on_delete=models.CASCADE, related_name='modifications')
    timestamp = models.DateTimeField(default=timezone.now)
    modification_type = models.CharField(max_length=50, choices=MODIFICATION_TYPES)
    description = models.TextField(help_text="Detailed description of the modification")
    
    # Optional: what was the goal/problem being addressed
    goal = models.CharField(
        max_length=200, blank=True,
        help_text="What issue were you trying to fix or improve?"
    )
    
    # Optional: was it successful?
    success_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="How successful was this modification? (1-10)"
    )
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.reed.name} - {self.get_modification_type_display()} on {self.timestamp.strftime('%Y-%m-%d')}"

