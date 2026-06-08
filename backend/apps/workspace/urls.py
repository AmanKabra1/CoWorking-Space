from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('buildings', views.BuildingViewSet, basename='building')
router.register('floors', views.FloorViewSet, basename='floor')
router.register('rooms', views.RoomViewSet, basename='room')
router.register('desks', views.DeskViewSet, basename='desk')
router.register('parking-slots', views.ParkingSlotViewSet, basename='parking-slot')

urlpatterns = [
    path('', include(router.urls)),
]
