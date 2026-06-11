"""
AI service layer — provider-agnostic, orchestrated with LangGraph.

Supports two free providers; whichever API key is configured is used
(Groq preferred if both are set):
  - Groq        -> set GROQ_API_KEY   (Llama 3.3 70B, very fast, free tier)
  - Google      -> set GOOGLE_API_KEY (or GEMINI_API_KEY) (Gemini 1.5 Flash)

The chat flow runs through a small LangGraph StateGraph so the conversation
is a proper stateful graph (easy to extend with tools/steps later).
"""
import json
import logging
import re
from typing import TypedDict

from django.conf import settings
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)

GROQ_MODEL = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
GEMINI_MODEL = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')


def _google_key():
    return getattr(settings, 'GOOGLE_API_KEY', '') or getattr(settings, 'GEMINI_API_KEY', '')


def _select_provider():
    """Return ('groq'|'gemini', model_name). Groq wins if both keys are set."""
    if getattr(settings, 'GROQ_API_KEY', ''):
        return 'groq', GROQ_MODEL
    if _google_key():
        return 'gemini', GEMINI_MODEL
    raise RuntimeError(
        'No AI provider configured. Set GROQ_API_KEY or GOOGLE_API_KEY (or GEMINI_API_KEY).'
    )


def _normalize_history(history):
    """Convert stored Gemini-style history -> generic [{role, content}] (role: user|assistant)."""
    out = []
    for h in history or []:
        role = 'assistant' if h.get('role') == 'model' else 'user'
        parts = h.get('parts')
        content = (parts[0] if parts else h.get('content', '')) or ''
        out.append({'role': role, 'content': content})
    return out


# ─── Provider calls ───────────────────────────────────────

def _groq_chat(system, messages):
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{'role': 'system', 'content': system}, *messages],
        temperature=0.7,
        max_tokens=1024,
    )
    usage = getattr(resp, 'usage', None)
    return {
        'reply': resp.choices[0].message.content,
        'model': GROQ_MODEL,
        'input_tokens': getattr(usage, 'prompt_tokens', 0) if usage else 0,
        'output_tokens': getattr(usage, 'completion_tokens', 0) if usage else 0,
    }


def _gemini_chat(system, messages):
    import google.generativeai as genai
    genai.configure(api_key=_google_key())
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system,
        generation_config={'temperature': 0.7, 'top_p': 0.95, 'max_output_tokens': 1024},
    )
    history = [
        {'role': ('model' if m['role'] == 'assistant' else 'user'), 'parts': [m['content']]}
        for m in messages[:-1]
    ]
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]['content'])
    usage = getattr(response, 'usage_metadata', None)
    return {
        'reply': response.text,
        'model': GEMINI_MODEL,
        'input_tokens': getattr(usage, 'prompt_token_count', 0) if usage else 0,
        'output_tokens': getattr(usage, 'candidates_token_count', 0) if usage else 0,
    }


def _generate_text(prompt: str) -> str:
    """One-shot completion via the active provider (used for non-chat helpers)."""
    provider, _ = _select_provider()
    if provider == 'groq':
        return _groq_chat('You are a helpful assistant for a coworking SaaS.',
                          [{'role': 'user', 'content': prompt}])['reply']
    return _gemini_chat('You are a helpful assistant for a coworking SaaS.',
                        [{'role': 'user', 'content': prompt}])['reply']


# ─── LangGraph chat graph ─────────────────────────────────

class ChatState(TypedDict, total=False):
    system: str
    context: str
    messages: list   # [{role, content}] including the latest user turn
    result: dict


def _respond_node(state: ChatState) -> ChatState:
    provider, _ = _select_provider()
    system = (
        f"{state['system']}\n\n"
        f"[Current platform data for your reference — do not repeat verbatim]\n{state.get('context', '')}"
    )
    fn = _groq_chat if provider == 'groq' else _gemini_chat
    return {'result': fn(system, state['messages'])}


_GRAPH = None


def _get_graph():
    global _GRAPH
    if _GRAPH is None:
        g = StateGraph(ChatState)
        g.add_node('respond', _respond_node)
        g.add_edge(START, 'respond')
        g.add_edge('respond', END)
        _GRAPH = g.compile()
    return _GRAPH


def chat_with_context(system_prompt: str, history: list, user_message: str, context: str) -> dict:
    """Run a chat turn through the LangGraph graph. Returns {reply, model, input_tokens, output_tokens}."""
    messages = [*_normalize_history(history), {'role': 'user', 'content': user_message}]
    state = _get_graph().invoke({'system': system_prompt, 'context': context, 'messages': messages})
    return state['result']


# ─── Helper generations (provider-agnostic) ───────────────

def get_booking_suggestions(context: str) -> dict:
    prompt = f"""You are a scheduling assistant for a coworking space.

{context}

Suggest 3–5 optimal booking time slots for this facility on this date.
For each slot provide start (HH:MM), end (HH:MM), duration_hours, estimated_cost, and a brief reason.
Avoid already-booked slots. Return ONLY a JSON array like:
[{{"start":"09:00","end":"11:00","duration_hours":2,"estimated_cost":1200,"reason":"Morning focus hours"}}]"""
    text = _generate_text(prompt).strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return {'suggestions': json.loads(match.group()), 'model': _select_provider()[1]}
        except json.JSONDecodeError:
            pass
    return {'suggestions': [], 'raw': text, 'model': _select_provider()[1]}


def generate_insights(data_context: str, insight_type: str) -> dict:
    type_prompts = {
        'bookings': 'Analyze the booking data and provide: (1) key patterns, (2) peak usage times, (3) booking revenue, (4) one actionable recommendation.',
        'invoices': 'Analyze the invoice/payment data and provide: (1) total revenue, (2) payment status breakdown, (3) overdue risk, (4) one collection recommendation.',
        'facilities': 'Analyze facility usage and provide: (1) most popular facility, (2) underutilised assets, (3) revenue opportunity, (4) one optimisation tip.',
    }
    instruction = type_prompts.get(insight_type, 'Analyze this coworking data and give a 4-point executive summary.')
    prompt = f"""{instruction}

Data:
{data_context}

Format:
**Summary**: (2 sentences)
**Key Findings**:
• Finding 1
• Finding 2
• Finding 3
**Recommendation**: (1 actionable suggestion)

Be specific with numbers. Under 200 words."""
    return {'insights': _generate_text(prompt), 'model': _select_provider()[1]}


def smart_search(query: str, available_filters: dict) -> dict:
    filters_desc = '\n'.join(f'  {k}: {v}' for k, v in available_filters.items())
    prompt = f"""You are a search query translator for a coworking SaaS API.

User query: "{query}"

Available filter fields:
{filters_desc}

Translate the query into a JSON object of filter key-value pairs. Only include clearly-implied filters.
Return ONLY valid JSON. Example: {{"status":"pending","booking_date":"2026-07-01"}}"""
    text = _generate_text(prompt).strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            filters = {k: v for k, v in json.loads(match.group()).items() if v is not None}
            return {'filters': filters, 'model': _select_provider()[1], 'original_query': query}
        except json.JSONDecodeError:
            pass
    return {'filters': {}, 'raw': text, 'model': _select_provider()[1], 'original_query': query}
