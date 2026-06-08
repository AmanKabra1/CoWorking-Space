from rest_framework.routers import DefaultRouter
from apps.community.views import PostViewSet, EventViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('events', EventViewSet, basename='event')

urlpatterns = router.urls
