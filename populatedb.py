import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from faker import Faker
from events.models import Category, Event, RSVP
from django.contrib.auth.models import User, Group
import random

fake = Faker()

# Categories
print("Creating categories...")
categories = []
for _ in range(5):
    cat = Category.objects.create(
        name=fake.word().capitalize(),
        description=fake.sentence()[:250]
    )
    categories.append(cat)
print(f"Created {len(categories)} categories")

# Events
print("\nCreating events...")
locations = ["DHAKA", "SYLHET", "CHOTTOGRAM", "RAJSHAHI", "MYMENSINGH", "RANGPUR", "KHULNA", "BARISHAL"]

# Organizer
organizer_group = Group.objects.filter(name='Organizer').first()
organizers = list(User.objects.filter(groups=organizer_group)) if organizer_group else []

for _ in range(20):
    Event.objects.create(
        name=fake.catch_phrase(),
        description=fake.text(max_nb_chars=200),
        date=fake.date_between(start_date='today', end_date='+60d'),
        time=fake.time(),
        location=random.choice(locations),
        category=random.choice(categories),
        image="images/events.jpeg",
        organizer=random.choice(organizers) if organizers else None,
    )
print(f"Created {Event.objects.count()} events")

# Users
print("\nCreating users...")
users = []
user_group, _ = Group.objects.get_or_create(name='User')

for _ in range(30):
    user = User.objects.create_user(
        username=fake.unique.user_name(),
        email=fake.unique.email(),
        password="password123",
        is_active=True, 
    )
    user.groups.add(user_group)
    users.append(user)
print(f"Created {len(users)} users")

# RSVPs
print("\nCreating RSVPs...")
events = list(Event.objects.all())
rsvp_count = 0

for user in users:
    chosen_events = random.sample(events, k=random.randint(1, 5))
    for event in chosen_events:
        rsvp, created = RSVP.objects.get_or_create(
            user=user,
            event=event,
            defaults={'is_confirmed': True} 
        )
        if created:
            rsvp_count += 1

print(f"Created {rsvp_count} RSVPs (all confirmed)")
print("\nAll data populated successfully!")