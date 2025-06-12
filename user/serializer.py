from rest_framework import serializers
from .models import CustomUser,FriendRequest

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'username', 'email', 'profile_pic', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Prevent password exposure

    def validate(self, attrs):
        
        password = attrs.get('password')
        email = attrs.get('email')
        username = attrs.get('username')

        if not username:
            raise serializers.ValidationError({'username': 'Username is required.'})
        if password and len(password) < 6:
            raise serializers.ValidationError({'password': 'Password must be at least 6 characters long.'})

        
        if email:
            serializers.EmailField().run_validation(email)
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': 'Email already exists.'})

        
        if username and CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username already exists.'})

        return super().validate(attrs)
    



class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = CustomUserSerializer(read_only=True)
    to_user = CustomUserSerializer(read_only=True)

    from_user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), source='from_user', write_only=True)
    to_user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), source='to_user', write_only=True)

    class Meta:
        model = FriendRequest
        fields = [
            'id',
            'from_user', 'to_user',
            'from_user_id', 'to_user_id',
            'is_accepted', 'created_at'
        ]
        read_only_fields = ['id', 'is_accepted', 'created_at']