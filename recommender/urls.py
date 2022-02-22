from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('best/', views.searchform_get, name='best'),
    path('bestp/', views.searchform_post, name='bestp'),
    path('home/', views.home, name="home"),
    path('profile/<user_id>', views.profile, name="profile"),
    path('profile/<user_id>/topsongs/', views.topSongs, name="topsongs")
]
 