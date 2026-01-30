import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from faker import Faker
from events.models import Category, Event, Participant
import random
from datetime import date, time

fake = Faker()

print("Creating categories...")
categories = []
for _ in range(5):
    cat = Category.objects.create(
        name=fake.word().capitalize(),
        description=fake.sentence()
    )
    categories.append(cat)
print(f"Created {len(categories)} categories")

print("\nCreating events...")
locations = ["DHAKA", "SYLHET", "CHOTTOGRAM", "RAJSHAHI", "MYMENSINGH", "RANGPUR", "KHULNA", "BARISHAL"]

for _ in range(20):
    Event.objects.create(
        name=fake.catch_phrase(),
        description=fake.text(max_nb_chars=200),
        date=fake.date_between(start_date='today', end_date='+60d'),
        time=fake.time(),
        location=random.choice(locations),
        category=random.choice(categories),
        image="image/events.jpeg"  
    )
print(f"Created {Event.objects.count()} events")

print("\nCreating participants...")
for _ in range(30):
    Participant.objects.create(
        name=fake.name(),
        email=fake.unique.email()  
    )
print(f"Created {Participant.objects.count()} participants")

print("\n All data populated successfully!")