from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from apps.community.models import Post, Comment, Event, EventRSVP
from apps.community.serializers import (
    PostSerializer, CommentSerializer, EventSerializer, EventRSVPSerializer
)
from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin


def _post_q(user):
    if user.is_super_admin:
        return Q()
    return Q(company=user.company) | Q(visibility=Post.PLATFORM)


def _event_q(user):
    if user.is_super_admin:
        return Q()
    return Q(company=user.company) | Q(is_public=True)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        return (
            Post.objects.filter(_post_q(self.request.user))
            .select_related('author', 'company')
            .prefetch_related('comments')
        )

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsSuperAdminOrCompanyAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        qs = post.comments.filter(is_deleted=False).select_related('author')
        return Response(CommentSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data={**request.data, 'post': post.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return (
            Event.objects.filter(_event_q(self.request.user))
            .select_related('organizer', 'company')
            .prefetch_related('rsvps')
        )

    @action(detail=True, methods=['post'])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        rsvp_status = request.data.get('status', EventRSVP.ATTENDING)
        if rsvp_status not in dict(EventRSVP.STATUS_CHOICES):
            return Response({'detail': 'Invalid status.'}, status=400)

        rsvp, created = EventRSVP.objects.update_or_create(
            event=event, user=request.user,
            defaults={'status': rsvp_status},
        )
        return Response(
            EventRSVPSerializer(rsvp).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        event = self.get_object()
        rsvps = event.rsvps.filter(status=EventRSVP.ATTENDING).select_related('user')
        return Response(EventRSVPSerializer(rsvps, many=True).data)
