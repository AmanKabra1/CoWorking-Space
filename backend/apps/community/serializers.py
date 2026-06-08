from rest_framework import serializers
from apps.community.models import Post, Comment, Event, EventRSVP


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'content', 'is_deleted', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'is_deleted', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'post_type', 'title', 'content', 'author', 'author_name',
            'company', 'company_name', 'visibility', 'is_pinned', 'comment_count', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'author_name', 'company', 'company_name', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        validated_data['company'] = user.company
        return super().create(validated_data)


class EventRSVPSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = EventRSVP
        fields = ['id', 'event', 'user', 'user_name', 'status', 'updated_at']
        read_only_fields = ['id', 'user', 'user_name', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    rsvp_count = serializers.IntegerField(read_only=True)
    my_rsvp = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_datetime', 'end_datetime', 'location',
            'organizer', 'organizer_name', 'company', 'company_name',
            'max_attendees', 'is_public', 'rsvp_count', 'my_rsvp',
        ]
        read_only_fields = ['id', 'organizer', 'organizer_name', 'company', 'company_name', 'rsvp_count']

    def get_organizer_name(self, obj):
        return obj.organizer.get_full_name() or obj.organizer.email

    def get_my_rsvp(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        rsvp = obj.rsvps.filter(user=request.user).first()
        return rsvp.status if rsvp else None

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['organizer'] = user
        validated_data['company'] = user.company
        return super().create(validated_data)
