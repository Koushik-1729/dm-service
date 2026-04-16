from prometheus_client import Counter, Histogram, Info

APP_INFO = Info("marketing_service", "Marketing Service Info")

REQUEST_COUNT = Counter(
    "marketing_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "marketing_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

AI_CALL_COUNT = Counter(
    "marketing_ai_calls_total",
    "Total AI provider calls",
    ["provider", "model", "layer"],
)

AI_CALL_LATENCY = Histogram(
    "marketing_ai_call_duration_seconds",
    "AI provider call latency",
    ["provider", "layer"],
)

WHATSAPP_MESSAGES_SENT = Counter(
    "marketing_whatsapp_messages_sent_total",
    "Total WhatsApp messages sent",
    ["message_type"],
)

CONTENT_GENERATED = Counter(
    "marketing_content_generated_total",
    "Total content pieces generated",
    ["channel", "content_type"],
)

LEADS_CAPTURED = Counter(
    "marketing_leads_captured_total",
    "Total leads captured",
    ["source_channel"],
)
