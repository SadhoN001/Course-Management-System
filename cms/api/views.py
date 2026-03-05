from django.shortcuts import render
from .models import User, Course, Lesson, Enrollment, LessonProgress
from .serializers import (RegisterSerializer, UserSerializer, LoginSerializer, LogoutSerializer, CourseSerializer,
        LessonSerializer, EnrollmentSerializer, LessonProgressSerializer )
from .permissions import IsInstructor, IsOwnerInstructor, IsOwnerInstructorOfLesson
from django.contrib.auth import get_user_model, authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
def get_tokens_for_user(user):
    """Generate refresh and access tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            serializer = LoginSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = User.objects.filter(email=email).first()
            if not user:
                    return Response({'error': 'Invalid email or password'},status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=user.username, password=password)

            if not user:
                return Response({'error': 'Invalid email or password'},status=status.HTTP_400_BAD_REQUEST)

            tokens = get_tokens_for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user' : {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    'error': 'Something went wrong',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = LogoutSerializer(data= request.data)
            serializer.is_valid(raise_exception=True)
            
            refresh_token = serializer.validated_data["refresh"]
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Logout Succesful'}, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
# course part----------->

class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'description']
    
class CourseDetailView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    
class CourseCreateView(CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def perform_create(self, serializer): # course create korar somoy instructor e automatic current login-user assign hobe
        serializer.save(instructor = self.request.user )
        
class CourseManageView(RetrieveUpdateDestroyAPIView): # instructor can Manage own courses
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerInstructor]
    
#lesson part------>
class LessonCreateView(CreateAPIView):
    serializer_class =  LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.instructor != self.request.user:
            raise PermissionDenied("You can only add lessons to your own courses")
        serializer.save()

class LessonListView(ListAPIView):
    serializer_class =  LessonSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(course_id = course_id).order_by('order')
    
class LessonManageView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class =  LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerInstructorOfLesson]
    
# Enrollment part--->
class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        course = Course.objects.filter(id= course_id).first()
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        enrollment, created = Enrollment.objects.get_or_create(student = request.user, course = course)
        if not created:
            return Response({"message": "Already enrolled"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MyEnrollmentsView(ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
    
# lesson progress--->

class MarkLessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, lesson_id):
        lesson = Lesson.objects.filter(id=lesson_id).first()
        
        if not lesson:
            raise NotFound("Lesson Not Found")
        is_enrolled = Enrollment.objects.filter(
            student = request.user,
            course = lesson.course
        ).exists()
        
        if not is_enrolled:
            raise PermissionDenied("You are not enrolled in this course")

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({
            "message": "Lesson marked as completed"
        }, status=status.HTTP_200_OK)

class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound("Course not found")
    
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()

        if not is_enrolled:
            raise PermissionDenied("You are not enrolled in this course")
        total_lessons = course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).count()
        percentage = 0
        if total_lessons > 0:
            percentage = (completed_lessons / total_lessons) * 100
        return Response({
            "course": course.title,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": round(percentage, 2)
        })