import logging
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIConversation
from .serializers import (
    ChatMessageSerializer, ChatResponseSerializer,
    BookingSuggestionSerializer, InsightsSerializer, SmartSearchSerializer,
    AIConversationSerializer,
)
from . import services, context as ctx

logger = logging.getLogger(__name__)


class AIChatView(APIView):
    """
    POST /api/v1/ai/chat/

    Multi-turn conversational AI assistant.
    Injects live company data into every prompt (RAG-lite pattern).
    Maintains conversation history across turns via session_id.
    Powered by Google Gemini 1.5 Flash (free tier: 15 RPM, 1500 RPD).
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChatMessageSerializer,
        responses={200: ChatResponseSerializer},
        tags=['AI Assistant'],
        summary='Chat with the AI assistant',
        description=(
            'Send a message to CoWorkHub AI. The assistant has real-time context '
            'about your bookings, facilities, and invoices. '
            'Provide session_id to continue an existing conversation.'
        ),
    )
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        conversation = None
        if session_id:
            conversation = AIConversation.objects.filter(id=session_id, user=user).first()

        if not conversation:
            conversation = AIConversation.objects.create(
                user=user,
                company=user.company,
                session_type=AIConversation.CHAT,
            )

        try:
            system_prompt = ctx.build_system_prompt(user)
            live_context = ctx.build_company_context(user)
            history = conversation.get_history_for_gemini()

            result = services.chat_with_context(
                system_prompt=system_prompt,
                history=history,
                user_message=message,
                context=live_context,
            )

            conversation.add_message('user', message)
            conversation.add_message('model', result['reply'])
            conversation.total_tokens += result.get('input_tokens', 0) + result.get('output_tokens', 0)
            conversation.save(update_fields=['messages', 'total_tokens', 'updated_at'])

            return Response({
                'session_id': conversation.id,
                'reply': result['reply'],
                'model': result['model'],
            })

        except Exception as e:
            logger.error('AI chat error: %s', e, exc_info=True)
            return Response(
                {'detail': f'AI service error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class BookingSuggestionsView(APIView):
    """
    POST /api/v1/ai/booking-suggestions/

    AI-powered slot recommendations for a facility on a specific date.
    Returns 3-5 optimal time windows with cost estimates and reasoning.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=BookingSuggestionSerializer,
        tags=['AI Assistant'],
        summary='Get AI booking slot suggestions',
    )
    def post(self, request):
        serializer = BookingSuggestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.facilities.models import Facility
        facility_id = serializer.validated_data['facility_id']
        date = serializer.validated_data['date']

        if date < timezone.localdate():
            return Response(
                {'detail': 'Date cannot be in the past.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            facility = Facility.objects.get(id=facility_id, is_active=True)
        except Facility.DoesNotExist:
            return Response({'detail': 'Facility not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            context_str = ctx.build_booking_suggestions_context(facility, date)
            result = services.get_booking_suggestions(context_str)
            return Response({'facility': facility.name, 'date': date, **result})
        except Exception as e:
            logger.error('Booking suggestions error: %s', e, exc_info=True)
            return Response(
                {'detail': f'AI service error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class InsightsView(APIView):
    """
    POST /api/v1/ai/insights/

    AI-generated plain-English analysis of bookings, invoices, or facility usage.
    Super Admin sees platform-wide data; Company Admin sees own company.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=InsightsSerializer,
        tags=['AI Assistant'],
        summary='Generate AI analytics insights',
    )
    def post(self, request):
        serializer = InsightsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        insight_type = serializer.validated_data['insight_type']
        date_from = serializer.validated_data.get('date_from')
        date_to = serializer.validated_data.get('date_to')

        try:
            data_context = self._build_data_context(user, insight_type, date_from, date_to)
            result = services.generate_insights(data_context, insight_type)
            return Response(result)
        except Exception as e:
            logger.error('Insights error: %s', e, exc_info=True)
            return Response(
                {'detail': f'AI service error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def _build_data_context(self, user, insight_type, date_from, date_to):
        from apps.bookings.models import Booking
        from apps.billing.models import Invoice
        from apps.facilities.models import Facility

        qs_filter = {} if user.is_super_admin else {'company': user.company}
        lines = []

        if insight_type == 'bookings':
            qs = Booking.objects.filter(**qs_filter)
            if date_from:
                qs = qs.filter(booking_date__gte=date_from)
            if date_to:
                qs = qs.filter(booking_date__lte=date_to)
            total = qs.count()
            by_status = {s: qs.filter(status=s).count() for s in [
                Booking.PENDING, Booking.APPROVED, Booking.COMPLETED,
                Booking.CANCELLED, Booking.REJECTED,
            ]}
            revenue = sum(b.total_amount for b in qs.filter(status=Booking.COMPLETED))
            top_facilities = {}
            for b in qs.select_related('facility'):
                top_facilities[b.facility.name] = top_facilities.get(b.facility.name, 0) + 1
            top = sorted(top_facilities.items(), key=lambda x: -x[1])[:5]
            lines += [
                f'Total bookings: {total}',
                f'By status: {by_status}',
                f'Revenue from completed: Rs {revenue}',
                f'Top 5 facilities: {top}',
            ]

        elif insight_type == 'invoices':
            qs = Invoice.objects.filter(**qs_filter)
            if date_from:
                qs = qs.filter(billing_period_start__gte=date_from)
            if date_to:
                qs = qs.filter(billing_period_end__lte=date_to)
            by_status = {s: qs.filter(status=s).count() for s in [
                Invoice.DRAFT, Invoice.SENT, Invoice.PAID, Invoice.OVERDUE, Invoice.CANCELLED
            ]}
            total_billed = sum(i.total_amount for i in qs)
            total_paid = sum(i.total_amount for i in qs.filter(status=Invoice.PAID))
            rate = f'{(total_paid / total_billed * 100):.1f}%' if total_billed else 'N/A'
            lines += [
                f'Total invoices: {qs.count()}',
                f'By status: {by_status}',
                f'Total billed: Rs {total_billed}',
                f'Total collected: Rs {total_paid}',
                f'Collection rate: {rate}',
            ]

        elif insight_type == 'facilities':
            bk_qs = Booking.objects.filter(**qs_filter, status=Booking.COMPLETED)
            usage = {}
            for f in Facility.objects.filter(is_active=True):
                count = bk_qs.filter(facility=f).count()
                rev = sum(b.total_amount for b in bk_qs.filter(facility=f))
                usage[f.name] = {'bookings': count, 'revenue': float(rev), 'capacity': f.capacity}
            lines.append(f'Facility usage: {usage}')

        return '\n'.join(lines)


class SmartSearchView(APIView):
    """
    POST /api/v1/ai/smart-search/

    Translate natural language into structured API filter parameters.
    "show me rejected bookings last week" → {"status": "rejected", "booking_date__gte": "..."}
    """
    permission_classes = [permissions.IsAuthenticated]

    FILTER_SCHEMAS = {
        'bookings': {
            'status': 'pending | approved | rejected | cancelled | completed',
            'booking_date': 'exact date YYYY-MM-DD',
            'booking_date__gte': 'on or after date YYYY-MM-DD',
            'booking_date__lte': 'on or before date YYYY-MM-DD',
            'facility__name__icontains': 'facility name contains text',
        },
        'invoices': {
            'status': 'draft | sent | paid | overdue | cancelled',
            'billing_period_start': 'period start YYYY-MM-DD',
            'due_date__lte': 'due on or before YYYY-MM-DD',
            'invoice_number__icontains': 'invoice number contains text',
        },
        'facilities': {
            'facility_type': 'conference_room | meeting_room | event_hall | podcast_studio | printing_room | 3d_printer | cafeteria | other',
            'name__icontains': 'name contains text',
            'capacity__gte': 'minimum capacity (integer)',
            'is_active': 'true or false',
        },
    }

    @extend_schema(
        request=SmartSearchSerializer,
        tags=['AI Assistant'],
        summary='Natural language → API filter translation',
    )
    def post(self, request):
        serializer = SmartSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['query']
        resource = serializer.validated_data['resource']

        try:
            result = services.smart_search(query, self.FILTER_SCHEMAS.get(resource, {}))
            return Response({
                'resource': resource,
                **result,
                'usage_hint': f'Apply these filters to GET /api/v1/{resource}/',
            })
        except Exception as e:
            logger.error('Smart search error: %s', e, exc_info=True)
            return Response(
                {'detail': f'AI service error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


@extend_schema(tags=['AI Assistant'], summary='List AI conversation history')
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_history(request):
    """GET /api/v1/ai/conversations/ — recent AI sessions for the current user."""
    convs = AIConversation.objects.filter(user=request.user).order_by('-created_at')[:20]
    return Response(AIConversationSerializer(convs, many=True).data)
