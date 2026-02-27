from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (RegisterView, LoginView, LogoutView, CourseListView, CourseDetailView, CourseCreateView, 
    CourseManageView, LessonCreateView, LessonListView, LessonManageView, EnrollCourseView, MyEnrollmentsView,
    MarkLessonCompleteView, CourseProgressView
    )

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    #course part
    path('courses/', CourseListView.as_view()),
    path('courses/<int:pk>', CourseDetailView.as_view()),
    path('courses/create/', CourseCreateView.as_view()),
    path('courses/manage/<int:pk>', CourseManageView.as_view()),
    
    #Lesson part
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lessons/manage/<int:pk>', LessonManageView.as_view(), name='lesson-manage'),
    
    #Enrollment part
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='course-enroll'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    
    # lesson progress
    # Progress APIs
    path('lessons/<int:lesson_id>/complete/', MarkLessonCompleteView.as_view(), name='lesson-complete'),
    path('courses/<int:course_id>/progress/', CourseProgressView.as_view(), name='course-progress'),
        
    
]
