from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.conf import settings
from datetime import date
from events.form import EventForm
from events.models import Event, Category, RSVP


def is_organizer(user):
    return user.is_authenticated and user.groups.filter(name='Organizer').exists()

def is_admin(user):
    return user.is_authenticated and (user.groups.filter(name='Admin').exists() or user.is_superuser)


#HOME 
def home(request):
    events = Event.objects.select_related('category').prefetch_related('rsvps')

    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(name__icontains=search_query)

    location = request.GET.get('location', '')
    if location:
        events = events.filter(location=location)

    # RSVP's confirmed
    user_rsvp_event_ids = set()
    if request.user.is_authenticated:
        user_rsvp_event_ids = set(
            RSVP.objects.filter(user=request.user, is_confirmed=True).values_list('event_id', flat=True)
        )

    context = {
        'events': events,
        'locations': Event.LOCATION_CHOICES,
        'search_query': search_query,
        'selected_location': location,
        'user_rsvp_event_ids': user_rsvp_event_ids,
    }
    return render(request, "home.html", context)


# RSVP FROM HOME
def quick_rsvp(request, event_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to RSVP for this event.")
        return redirect('sign-in')

    event = get_object_or_404(Event, id=event_id)

    # Organizer / admin parbe na RSVP
    if is_admin(request.user) or is_organizer(request.user):
        messages.info(request, "Organizers and admins cannot RSVP for events.")
        return redirect('home')

    existing = RSVP.objects.filter(user=request.user, event=event).first()
    if existing:
        if existing.is_confirmed:
            messages.info(request, "You have already RSVP'd for this event.")
        else:
            messages.info(request, "Please confirm your RSVP via the email we sent you.")
        return redirect('home')

    rsvp = RSVP.objects.create(user=request.user, event=event, is_confirmed=False)

    # Send confirmation email
    confirm_url = f"{settings.FRONTEND_URL}rsvp/confirm/{rsvp.token}/"
    send_mail(
        subject=f"Confirm your RSVP: {event.name}",
        message=(
            f"Hi {request.user.username},\n\n"
            f"Please confirm your RSVP for '{event.name}' by clicking the link below:\n"
            f"{confirm_url}\n\n"
            f"If you did not request this, ignore this email."
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=True,
    )
    messages.success(request, "A confirmation email has been sent. Please check your inbox to complete RSVP.")
    return redirect('home')


# RSVP CONFIRM
def confirm_rsvp(request, token):
    rsvp = get_object_or_404(RSVP, token=token)
    if not rsvp.is_confirmed:
        rsvp.is_confirmed = True
        rsvp.save()
        messages.success(request, f"Your RSVP for '{rsvp.event.name}' is confirmed!")
    else:
        messages.info(request, "Your RSVP was already confirmed.")
    return redirect('details', id=rsvp.event.id)


#DETAILS
def details(request, id):
    event = get_object_or_404(
        Event.objects.select_related('category', 'organizer').prefetch_related('rsvps__user'),
        id=id
    )

    user = request.user
    user_rsvp = None
    user_has_rsvpd = False
    rsvp_confirmed = False

    if user.is_authenticated:
        user_rsvp = RSVP.objects.filter(user=user, event=event).first()
        if user_rsvp:
            user_has_rsvpd = True
            rsvp_confirmed = user_rsvp.is_confirmed

    #RSVP details page
    if request.method == 'POST' and request.POST.get('action') == 'rsvp':
        if not user.is_authenticated:
            messages.warning(request, "Please log in to RSVP.")
            return redirect('sign-in')
        if is_admin(user) or is_organizer(user):
            messages.info(request, "Organizers/admins cannot RSVP.")
            return redirect('details', id=id)
        if user_rsvp:
            messages.info(request, "You have already RSVP'd for this event.")
            return redirect('details', id=id)

        rsvp = RSVP.objects.create(user=user, event=event, is_confirmed=False)
        confirm_url = f"{settings.FRONTEND_URL}rsvp/confirm/{rsvp.token}/"
        send_mail(
            subject=f"Confirm your RSVP: {event.name}",
            message=(
                f"Hi {user.username},\n\n"
                f"Click to confirm your RSVP for '{event.name}':\n{confirm_url}\n\n"
                f"Thank you!"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
        messages.success(request, "Confirmation email sent! Please check your inbox.")
        return redirect('details', id=id)

    # RSVP list
    show_rsvp_list = False
    show_rsvp_button = False

    if user.is_authenticated:
        if is_admin(user):
            show_rsvp_list = True
            show_rsvp_button = False  # admin doesn't RSVP
        elif is_organizer(user):
            show_rsvp_list = True
            # Show RSVP button 
            show_rsvp_button = (event.organizer != user)
        else:
            # Normal user
            show_rsvp_list = False
            show_rsvp_button = not user_has_rsvpd

    confirmed_rsvps = event.rsvps.filter(is_confirmed=True).select_related('user')

    context = {
        'event': event,
        'confirmed_rsvps': confirmed_rsvps,
        'rsvp_count': confirmed_rsvps.count(),
        'user_has_rsvpd': user_has_rsvpd,
        'rsvp_confirmed': rsvp_confirmed,
        'show_rsvp_list': show_rsvp_list,
        'show_rsvp_button': show_rsvp_button,
        'is_admin': is_admin(user) if user.is_authenticated else False,
        'is_organizer': is_organizer(user) if user.is_authenticated else False,
    }
    return render(request, "details.html", context)


#DASHBOARD 
@login_required
def dashboard(request):
    user = request.user
    today = date.today()

    # Admin dashboard
    if is_admin(user):
        if request.method == 'POST' and request.POST.get('action') == 'delete_event':
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            event.delete()
            messages.success(request, f"Event deleted successfully!")
            return redirect('dashboard')

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

        events = events.select_related('category').annotate(rsvp_count=Count('rsvps')).order_by('-date', '-time')

        context = {
            'role': 'admin',
            'total_rsvps': RSVP.objects.filter(is_confirmed=True).count(),
            'total_events': Event.objects.count(),
            'upcoming_events_count': Event.objects.filter(date__gte=today).count(),
            'past_events_count': Event.objects.filter(date__lt=today).count(),
            'events': events,
            'filter_type': filter_type,
            'title': title,
        }
        return render(request, "dashboard.html", context)

    # Organizer dashboard 
    elif is_organizer(user):
        if request.method == 'POST' and request.POST.get('action') == 'delete_event':
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id, organizer=user)
            event.delete()
            messages.success(request, "Event deleted successfully!")
            return redirect('dashboard')

        my_events = Event.objects.filter(organizer=user).select_related('category').annotate(
            rsvp_count=Count('rsvps', filter=Q(rsvps__is_confirmed=True))
        ).order_by('-date')

        total_participants = RSVP.objects.filter(event__organizer=user, is_confirmed=True).count()
        upcoming_events = my_events.filter(date__gte=today)
        past_events = my_events.filter(date__lt=today)

        context = {
            'role': 'organizer',
            'my_events': my_events,
            'total_participants': total_participants,
            'total_events': my_events.count(),
            'upcoming_events': upcoming_events,
            'past_events': past_events,
        }
        return render(request, "dashboard.html", context)

    # User dashboard
    else:
        user_rsvps = RSVP.objects.filter(user=user, is_confirmed=True).select_related('event').order_by('-rsvp_date')
        context = {
            'role': 'user',
            'user_rsvps': user_rsvps,
        }
        return render(request, "dashboard.html", context)


# CREATE AND UPDATE EVENT
@login_required
def create_event(request):
    if not (is_admin(request.user) or is_organizer(request.user)):
        messages.error(request, "You don't have permission to create events.")
        return redirect('home')

    event_id = request.GET.get('update')
    event = None

    if event_id:
        if is_admin(request.user):
            event = get_object_or_404(Event, id=event_id)
        else:
            event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            saved_event = form.save(commit=False)
            use_existing = form.cleaned_data.get('use_existing_category')

            if use_existing:
                saved_event.category = form.cleaned_data.get('existing_category')
            else:
                category = Category.objects.create(
                    name=form.cleaned_data.get('new_category_name'),
                    description=form.cleaned_data.get('new_category_description', '')
                )
                saved_event.category = category
                messages.success(request, f"Category '{category.name}' created!")

            if not event:
                saved_event.organizer = request.user
            saved_event.save()
            action = 'updated' if event else 'created'
            messages.success(request, f"Event '{saved_event.name}' {action} successfully!")
            return redirect('dashboard')

    else: 
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {
        'event_form': form,
        'action': 'Update' if event else 'Create',
        'button_text': 'Update Event' if event else 'Create Event',
        'event': event,
    })