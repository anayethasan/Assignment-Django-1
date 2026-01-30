from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(max_length=250)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Participant(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    events = models.ManyToManyField('Event', related_name='participants', blank=True)
    
    def __str__(self):
        return self.name

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
    
    image = models.CharField(max_length=250, default='image/events.jpeg', blank=True)
    name = models.CharField(max_length=250)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=250, choices=LOCATION_CHOICES, default="DHAKA")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    
    def __str__(self):
        return self.name