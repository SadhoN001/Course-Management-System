from rest_framework import serializers
from .models import User, Course, Lesson, Enrollment, LessonProgress
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = True, validators = [validate_password])
    password2 = serializers.CharField(write_only = True, required = True)
    bio = serializers.CharField(required=False)  
    avatar = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'password', 'password2', 'bio', 'avatar')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Password must match'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2') # password2 confitmationer jonno..database save korar dorkar nai tai remove.
        user = User.objects.create_user(
            username= validated_data['username'],
            email=validated_data.get('email'),
            password= validated_data['password'],
            role=validated_data.get('role', 'student'),
            bio=validated_data.get('bio', ''),
            avatar=validated_data.get('avatar', None),
        )
        return user
    
class UserSerializer(serializers.ModelSerializer): # emni banai rakhsi
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'bio', 'avatar')
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True, write_only = True)
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only = True)
    lesson_count = serializers.ReadOnlyField()
    enrollment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'instructor', 'lesson_count', 'enrollment_count', 'created_at']
        
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'video_url', 'duration', 'order']
        
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']
        read_only_fields = ['student', 'enrolled_at']
        
class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['id', 'student', 'lesson', 'completed', 'completed_at']
        read_only_fields = ['student', 'completed_at']