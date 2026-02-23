from django.db import models
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Event(models.Model):
    LOCATION_CHOICES = [
        ("DHAKA", "Dhaka"),
        ("SYLHET", "Sylhet"),
        ("CHOTTOGRAM", "Chottogram"),
        ("RAJSHAHI", "Rajshahi"),
        ("MYMENSINGH", "Mymensingh"),
        ("RANGPUR", "Rangpur"),
        ("KHULNA", "Khulna"),
        ("BARISHAL", "Barishal")
    ]

    image = models.ImageField(upload_to='images/events/', default='images/events.jpeg', blank=True)
    name = models.CharField(max_length=250)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=250, choices=LOCATION_CHOICES, default="DHAKA")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    #organizer field
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events'
    )

    def __str__(self):
        return self.name

    @property
    def participant_count(self):
        return self.rsvps.filter(is_confirmed=True).count()


class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    rsvp_date = models.DateTimeField(auto_now_add=True)

    #email confirmation field
    is_confirmed = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'event'], name='unique_user_event_rsvp')
        ]
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"

    def __str__(self):
        return f"{self.user.username} --> {self.event.name}"