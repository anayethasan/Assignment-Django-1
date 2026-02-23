from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
from users.forms import CustomRegistrationForm, LoginForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch


def is_admin(user):
    return user.is_authenticated and (user.groups.filter(name='Admin').exists() or user.is_superuser)


#SIGN UP
def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # saves with is_active=False
            messages.success(request, 'Registration successful! Please check your email to activate your account.')
            return redirect('sign-in')
        # if invalid
    return render(request, 'sign-in_sign-up.html', {"form": form, "show_signup": True})


#SIGN IN
def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'sign-in_sign-up.html', {'form': form, 'show_signup': False})


#SIGN OUT
@login_required
def sign_out(request):
    logout(request)
    return redirect('home')


#ACTIVATE USER 
def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated! Please log in.")
            return redirect('sign-in')
        else:
            return HttpResponse('<h2>Invalid or expired activation link.</h2>')
    except User.DoesNotExist:
        return HttpResponse('<h2>User not found.</h2>')


#USER LIST (Admin only)
@user_passes_test(is_admin, login_url='no-permission')
def user_list(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all().order_by('username')

    for u in users:
        if u.all_groups:
            u.group_name = u.all_groups[0].name
        else:
            u.group_name = 'No Role Assigned'

    return render(request, 'admin/user_list.html', {'users': users})


#ASSIGN ROLE (Admin only)
@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    target_user = get_object_or_404_user(user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            target_user.groups.clear()
            target_user.groups.add(role)
            messages.success(request, f"User '{target_user.username}' has been assigned to '{role.name}' role.")
            return redirect('user-list')

    return render(request, 'admin/assign_role.html', {'form': form, 'target_user': target_user})


def get_object_or_404_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("User not found")


#CREATE GROUP (Admin can do)
@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group-list')
    return render(request, 'admin/create_group.html', {'form': form})


#GROUP LIST (Admin can do) 
@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})

#DELETE USER (Admin can do) 
@user_passes_test(is_admin, login_url='no-permission')
def delete_user(request, user_id):
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("User not found")
    if target_user.is_superuser:
        messages.error(request, "Superuser cannot be deleted.")
        return redirect('user-list')
    
    username = target_user.username
    target_user.delete()
    messages.success(request, f"User '{username}' deleted successfully.")
    return redirect('user-list')