"""
AI service layer — wraps Google Gemini API with fallback handling.
Free tier: gemini-1.5-flash — 15 RPM, 1M TPM, 1500 RPD (no billing required).
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_MODEL = 'gemini-1.5-flash'


def _get_model():
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'max_output_tokens': 1024,
            },
            safety_settings=[
                {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            ],
        )
    except ImportError:
        raise RuntimeError('google-generativeai package not installed. Run: pip install google-generativeai')


def chat_with_context(system_prompt: str, history: list, user_message: str, context: str) -> dict:
    """
    Send a message to Gemini with injected company context.

    Args:
        system_prompt: Persona + role context (set once at start of session)
        history: Previous [{role, parts}] messages for multi-turn conversation
        user_message: The current user input
        context: Live DB data (bookings, invoices, facilities)

    Returns:
        {"reply": str, "model": str, "input_tokens": int, "output_tokens": int}
    """
    model = _get_model()

    enriched_message = (
        f"[Current platform data for your reference — do not repeat this block verbatim]\n"
        f"{context}\n\n"
        f"[User question]\n{user_message}"
    )

    full_history = [
        {'role': 'user', 'parts': [system_prompt]},
        {'role': 'model', 'parts': ['Understood. I am CoWorkHub Assistant, ready to help.']},
        *history,
    ]

    chat = model.start_chat(history=full_history)
    response = chat.send_message(enriched_message)

    usage = getattr(response, 'usage_metadata', None)
    return {
        'reply': response.text,
        'model': GEMINI_MODEL,
        'input_tokens': getattr(usage, 'prompt_token_count', 0),
        'output_tokens': getattr(usage, 'candidates_token_count', 0),
    }


def get_booking_suggestions(context: str) -> dict:
    """Ask AI for smart booking slot recommendations."""
    model = _get_model()
    prompt = f"""You are a scheduling assistant for a coworking space.

{context}

Suggest 3–5 optimal booking time slots for this facility on this date.
For each slot provide:
- Start time and end time (HH:MM format)
- Duration
- Estimated cost (based on the pricing above)
- Brief reason why this slot is a good choice

Avoid already-booked slots. Return a JSON array with this structure:
[
  {{
    "start": "09:00",
    "end": "11:00",
    "duration_hours": 2,
    "estimated_cost": 1200,
    "reason": "Morning focus hours, low demand"
  }}
]
Return ONLY the JSON array, no extra text."""

    response = model.generate_content(prompt)
    import json
    import re
    text = response.text.strip()
    # Extract JSON array from response
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            suggestions = json.loads(match.group())
            return {'suggestions': suggestions, 'model': GEMINI_MODEL}
        except json.JSONDecodeError:
            pass
    return {'suggestions': [], 'raw': text, 'model': GEMINI_MODEL}


def generate_insights(data_context: str, insight_type: str) -> dict:
    """Generate plain-English insights from structured data."""
    model = _get_model()

    type_prompts = {
        'bookings': 'Analyze the booking data below and provide: (1) key patterns, (2) peak usage times, (3) revenue from bookings, (4) one actionable recommendation.',
        'invoices': 'Analyze the invoice/payment data below and provide: (1) total revenue summary, (2) payment status breakdown, (3) overdue risk, (4) one collection recommendation.',
        'facilities': 'Analyze the facility usage below and provide: (1) most popular facility, (2) underutilised assets, (3) revenue opportunity, (4) one optimisation tip.',
    }

    instruction = type_prompts.get(insight_type, 'Analyze this coworking space data and provide a 4-point executive summary.')

    prompt = f"""{instruction}

Data:
{data_context}

Format your response as:
**Summary**: (2 sentences)
**Key Findings**:
• Finding 1
• Finding 2
• Finding 3
**Recommendation**: (1 actionable suggestion)

Be specific with numbers. Keep it under 200 words."""

    response = model.generate_content(prompt)
    usage = getattr(response, 'usage_metadata', None)
    return {
        'insights': response.text,
        'model': GEMINI_MODEL,
        'tokens': getattr(usage, 'total_token_count', 0),
    }


def smart_search(query: str, available_filters: dict) -> dict:
    """
    Translate natural language into structured filter parameters.
    available_filters: dict of field→description for the endpoint being searched.
    """
    model = _get_model()
    filters_desc = '\n'.join(f'  {k}: {v}' for k, v in available_filters.items())

    prompt = f"""You are a search query translator for a coworking SaaS API.

User query: "{query}"

Available filter fields:
{filters_desc}

Translate the user's query into a JSON object of filter key-value pairs.
Only include filters that are clearly implied by the query.
Use null for values you cannot determine.
Return ONLY valid JSON, no explanation.

Example output: {{"status": "pending", "booking_date": "2026-07-01"}}"""

    response = model.generate_content(prompt)
    import json
    import re
    text = response.text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            filters = {k: v for k, v in json.loads(match.group()).items() if v is not None}
            return {'filters': filters, 'model': GEMINI_MODEL, 'original_query': query}
        except json.JSONDecodeError:
            pass
    return {'filters': {}, 'raw': text, 'model': GEMINI_MODEL, 'original_query': query}
