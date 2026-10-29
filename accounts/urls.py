
from django.urls import path
from accounts.views import register,login_view,logout_view,profile_view,profile_edit,ChangePasswordView

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
]

