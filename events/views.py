from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date
from events.form import EventCategoryForm, ParticipantForm
from events.models import Event, Category, Participant

# Home

def home(request):
    events = Event.objects.select_related('category').prefetch_related('participants')
    
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(name__icontains=search_query)
    
    location = request.GET.get('location', '')
    if location:
        events = events.filter(location=location)
    
    locations = Event.LOCATION_CHOICES
    
    context = {
        'events': events,
        'locations': locations,
        'search_query': search_query,
        'selected_location': location,
    }
    return render(request, "home.html", context)

# Details

def details(request, id):
    event = get_object_or_404(
        Event.objects.select_related('category').prefetch_related('participants'),
        id=id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'join_event':
            form = ParticipantForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email')
                
                participant, created = Participant.objects.get_or_create(
                    email=email,
                    defaults={'name': name}
                )
                
                if event not in participant.events.all():
                    participant.events.add(event)
                    messages.success(request, f"{name} joined the event successfully!")
                else:
                    messages.info(request, f"{name} is already registered for this event.")
                
                return redirect('details', id=id)
        
        elif action == 'delete_participant':
            participant_id = request.POST.get('participant_id')
            participant = get_object_or_404(Participant, id=participant_id)
            
            participant.events.remove(event)
            
            if participant.events.count() == 0:
                participant_name = participant.name
                participant.delete()
                messages.success(request, f"Participant '{participant_name}' removed from this event.")
            else:
                messages.success(request, f"Participant '{participant.name}' removed from this event.")
            
            return redirect('details', id=id)
    
    participant_form = ParticipantForm()
    participants = event.participants.all()
    
    context = {
        'event': event,
        'participant_form': participant_form,
        'participants': participants,
    }
    return render(request, "details.html", context)

# Participant

def update_participant(request, event_id, participant_id):

    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Participant, id=participant_id)
    
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Participant '{participant.name}' updated successfully!")
            return redirect('details', id=event.id)
    else:
        form = ParticipantForm(instance=participant)
    
    context = {
        'event': event,
        'participant': participant,
        'form': form,
    }
    return render(request, 'edit_participant.html', context)

# DASHBOARD 

def dashboard(request):
    today = date.today()
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_event':
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            event_name = event.name
            event.delete()
            messages.success(request, f"Event '{event_name}' deleted successfully!")
            return redirect('dashboard')
        
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(date__gte=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()
    
    filter_type = request.GET.get('filter', 'today')
    
    if filter_type == 'all':
        events = Event.objects.all()
        title = "All Events"
    elif filter_type == 'upcoming':
        events = Event.objects.filter(date__gte=today)
        title = "Upcoming Events"
    elif filter_type == 'past':
        events = Event.objects.filter(date__lt=today)
        title = "Past Events"
    else:
        events = Event.objects.filter(date=today)
        title = "Today's Events"
    
    events = events.select_related('category').prefetch_related('participants').annotate(
        participant_count=Count('participants')
    ).order_by('-date', '-time')
    
    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events_count': upcoming_events_count,
        'past_events_count': past_events_count,
        'events': events,
        'filter_type': filter_type,
        'title': title,
    }
    return render(request, "dashboard.html", context)

# Create Events

def create_event(request):
    event_id = request.GET.get('update')
    event = None
    
    if event_id:
        event = get_object_or_404(Event, id=event_id)
        initial_data = {
            'event_name': event.name,
            'event_description': event.description,
            'event_date': event.date,
            'event_time': event.time,
            'event_location': event.location,
            'event_image': event.image,
            'use_existing_category': True,
            'existing_category': event.category,
        }
        event_form = EventCategoryForm(initial=initial_data)
        action = 'Update'
        button_text = 'Update Event'
    else:
        event_form = EventCategoryForm()
        action = 'Create'
        button_text = 'Create Event'
    
    if request.method == 'POST':
        event_form = EventCategoryForm(request.POST)
        
        if event_form.is_valid():
            data = event_form.cleaned_data
            
            use_existing = data.get('use_existing_category')
            
            if use_existing:
                category = data.get('existing_category')
            else:
                category = Category.objects.create(
                    name=data.get('new_category_name'),
                    description=data.get('new_category_description', '')
                )
                messages.success(request, f"Category '{category.name}' created!")
            
            if event:
                event.image = data.get('event_image') if data.get('event_image') else 'image/events.jpeg'
                event.name = data.get('event_name')
                event.description = data.get('event_description')
                event.date = data.get('event_date')
                event.time = data.get('event_time')
                event.location = data.get('event_location')
                event.category = category
                event.save()
                messages.success(request, f"Event '{event.name}' updated successfully!")
            else:
                event = Event.objects.create(
                    image=data.get('event_image') if data.get('event_image') else 'image/events.jpeg',
                    name=data.get('event_name'),
                    description=data.get('event_description'),
                    date=data.get('event_date'),
                    time=data.get('event_time'),
                    location=data.get('event_location'),
                    category=category
                )
                messages.success(request, f"Event '{event.name}' created successfully!")
            
            return redirect('dashboard')
    
    context = {
        'event_form': event_form,
        'action': action,
        'button_text': button_text,
        'event': event
    }
    return render(request, 'event_form.html', context)