from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import User
from .utils import make_avatar_file


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'avatar'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Password fields not match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        avatar = validated_data.pop('avatar', None)

        user = User.objects.create_user(**validated_data)

        if avatar:
            user.avatar = avatar
        else:
            display = user.get_full_name() or user.username
            user.avatar = make_avatar_file(display)

        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError('User not found')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password"')


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    posts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_received_count = serializers.SerializerMethodField()
    karma_points = serializers.IntegerField(read_only=True)
    karma_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'bio', 'created_at', 'updated_at',
            'posts_count', 'comments_count', 'likes_received_count',
            'karma_points', 'karma_level'
        )
        read_only_fields = ('id', 'created_at', 'updated_at',
                            'karma_points', 'karma_level', 'likes_received_count')

    def get_posts_count(self, obj):
        """Кількість пості"""
        try:
            return obj.posts.count()
        except AttributeError:
            return 0

    def get_comments_count(self, obj):
        """Кількість коментаріїв"""
        try:
            return obj.comments.count()
        except AttributeError:
            return 0

    def get_likes_received_count(self, obj):
        from django.contrib.contenttypes.models import ContentType
        from apps.likes.models import Like

        try:
            total = 0

            # Лайки на постах
            from apps.main.models import Post  # ← твій шлях до Post
            post_ct = ContentType.objects.get_for_model(Post)
            post_ids = list(obj.posts.values_list('id', flat=True))
            if post_ids:
                total += Like.objects.filter(
                    content_type=post_ct,
                    object_id__in=post_ids
                ).count()

            # Лайки на коментарях
            from apps.comments.models import Comment  # ← твій шлях до Comment
            comment_ct = ContentType.objects.get_for_model(Comment)
            comment_ids = list(obj.comments.values_list('id', flat=True))
            if comment_ids:
                total += Like.objects.filter(
                    content_type=comment_ct,
                    object_id__in=comment_ids
                ).count()

            return total

        except Exception as e:
            print(f"Error: {e}")
            return 0


class PublicUserSerializer(serializers.ModelSerializer):
    """Публічний профіль — без email та приватних даних"""
    full_name = serializers.ReadOnlyField()
    posts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'first_name', 'last_name',
            'avatar', 'bio', 'date_joined',
            'karma_points', 'karma_level',
            'posts_count', 'comments_count',
        )

    def get_posts_count(self, obj):
        try:
            return obj.posts.filter(status='published').count()
        except AttributeError:
            return 0

    def get_comments_count(self, obj):
        try:
            return obj.comments.count()
        except AttributeError:
            return 0


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'bio')
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True},
        }

    def update(self, instance, validated_data):
        # Якщо аватар не передають взагалі — не чіпаємо його
        if 'avatar' not in validated_data:
            pass

        # Якщо змінилось ім'я і не завантажили нову аватарку — регенеруємо
        new_first = validated_data.get('first_name', instance.first_name)
        new_last = validated_data.get('last_name', instance.last_name)
        new_full_name = f"{new_first} {new_last}".strip() or instance.username
        old_full_name = instance.get_full_name() or instance.username

        name_changed = new_full_name != old_full_name
        avatar_provided = 'avatar' in validated_data

        if name_changed and not avatar_provided:
            validated_data['avatar'] = make_avatar_file(new_full_name)

        # Якщо користувач передає нову аватарку — старий видалиться через сигнал
        if 'avatar' in validated_data and validated_data['avatar'] is None:
            # Хоче повністю видалити аватарку
            if instance.avatar:
                instance.avatar.delete(save=False)

        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,
                                         validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Password fields not match'})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
