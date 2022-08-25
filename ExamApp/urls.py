from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView,LoginView
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('', include('main.urls')),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='logout.html'),name='logout'),
]
