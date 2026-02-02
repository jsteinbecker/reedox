from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Thread(models.Model):
    """
    Represents thread used for wrapping reeds.
    """
    color = models.CharField(max_length=50, help_text="Thread color")
    gauge = models.CharField(max_length=50, blank=True, help_text="Thread gauge/thickness (optional)")
    
    class Meta:
        ordering = ['color']
    
    def __str__(self):
        if self.gauge:
            return f"{self.color} ({self.gauge})"
        return self.color


class Staple(models.Model):
    """
    Represents a staple/tube for reed construction.
    """
    MATERIAL_CHOICES = [
        ('brass', 'Brass'),
        ('nickel_silver', 'Nickel Silver'),
        ('silver', 'Silver'),
        ('copper', 'Copper'),
        ('other', 'Other'),
    ]
    
    SHAPE_CHOICES = [
        ('recessed', 'Recessed'),
        ('o_ring', 'O-Ring'),
        ('flat', 'Flat'),
        ('other', 'Other'),
    ]
    
    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES, help_text="Staple material")
    shape = models.CharField(max_length=50, choices=SHAPE_CHOICES, help_text="Staple shape")
    make = models.CharField(max_length=100, blank=True, help_text="Manufacturer/make (optional)")
    length_mm = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Staple length in mm (e.g., 47mm)"
    )
    
    # Track inventory
    quantity = models.IntegerField(default=1, help_text="Number of staples of this type in stock")
    
    class Meta:
        ordering = ['material', 'shape']
    
    def __str__(self):
        parts = [self.get_shape_display(), self.get_material_display()]
        if self.length_mm:
            parts.append(f"{self.length_mm}mm")
        if self.make:
            parts.append(self.make)
        result = " ".join(parts)
        if self.quantity > 1:
            result += f" (×{self.quantity})"
        return result


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
    
    name = models.CharField(max_length=100, blank=True, help_text="Name or identifier for this reed (optional)")
    thread = models.ForeignKey(Thread, on_delete=models.PROTECT, related_name='reeds', help_text="Thread used for this reed")
    staple = models.ForeignKey(Staple, on_delete=models.PROTECT, related_name='reeds', help_text="Staple used for this reed")
    created_date = models.DateTimeField(default=timezone.now, help_text="When the reed was created/started")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Reed construction details
    cane_source = models.CharField(max_length=200, blank=True, help_text="Source or brand of cane")
    shape = models.CharField(max_length=100, blank=True, help_text="Cane shape used for this reed")
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
    
    def save(self, *args, **kwargs):
        # Auto-generate name if not provided
        if not self.name:
            thread_name = str(self.thread)
            staple_name = f"{self.staple.get_shape_display()} {self.staple.get_material_display()}"
            self.name = f"{thread_name} / {staple_name}"
        super().save(*args, **kwargs)
    
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

