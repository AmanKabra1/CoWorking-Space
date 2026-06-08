from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.AIChatView.as_view(), name='ai-chat'),
    path('booking-suggestions/', views.BookingSuggestionsView.as_view(), name='ai-booking-suggestions'),
    path('insights/', views.InsightsView.as_view(), name='ai-insights'),
    path('smart-search/', views.SmartSearchView.as_view(), name='ai-smart-search'),
    path('conversations/', views.conversation_history, name='ai-conversations'),
]
