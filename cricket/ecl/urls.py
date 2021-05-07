"""cricket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.login_page, name="login"),
    path('inv_login/', views.invalid_login, name="inv_login"),
    path('register/', views.register_user, name="register"),
    path('register/success/', views.register_success, name="register_success"),
    path('login_auth/', views.login_auth, name="login_auth"),
    path('login_auth/home/', views.home_view, name="home"),
    path('join_match/', views.join_match_view, name="join_match"),
    path('join_match/process_req', views.join_match_processing, name="join_match_processing"),
    path('my_all_matches/', views.my_matches_list_view, name="my_all_matches"),
    path('match_submitted/', views.match_value_submission, name="match_submitted"),
    path('single_league_view/<league_id>', views.single_league_matches_view, name="single_league_view"),
    path('my_profile/', views.my_profile_view, name="my_profile_view"),
    path('logout/', views.logout_view, name="logout"),
]
