from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, user_list, assign_role, create_group, group_list, delete_user

urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate-user'),
    path('user-list/', user_list, name='user-list'),
    path('assign-role/<int:user_id>/', assign_role, name='assign-role'),
    path('create-group/', create_group, name='create-group'),
    path('groups/', group_list, name='group-list'),
    path('delete-user/<int:user_id>/', delete_user, name='delete-user'),
]