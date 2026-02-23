# from django.db.models.signals import m2m_changed, post_delete
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from events.models import Category, Event, RSVP


# @receiver(m2m_changed, sender=Event.event.through)
# def notify_organizer_on_event_creation(sender, instance, action, **kwargs):
#     print(instance, instance.user.all())
    
#     assigned_emails = [user.email for user in instance.event.all()]
#     print('Checking...', assigned_emails)
    
#     send_mail(
#         "New Task Assigned",
#         f"You have been assigned to the this task : --> {instance.title}",
#         "aestheticjersey.aj@gmail.com",
#         assigned_emails,
#         fail_silently=False,
#     )
    
# @receiver(post_delete, sender=Event)
# def  delete_associate_details(sender, instance, **kwargs):
#     if instance.rsvps:
#         print(isinstance)
#         instance.rsvps.delete()
        
#         print('Deleted Successfully!')