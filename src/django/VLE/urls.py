"""VLE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from VLE.views import get_user_courses
from VLE.views import get_course_assignments
from VLE.views import get_assignment_journals
from VLE.views import get_upcoming_deadlines

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/get_user_courses/', get_user_courses, name='get_user_courses'),
    path('api/get_course_assignments/<str:cID>/', get_course_assignments, name='get_course_assignments'),
    path('api/get_assignment_journals/<str:aID>/', get_assignment_journals, name='get_assignment_journals'),
    path('api/get_upcoming_deadlines/', get_upcoming_deadlines, name='get_upcoming_deadlines'),
]