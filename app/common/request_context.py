from contextvars import ContextVar

client_phone_ctx: ContextVar[str | None] = ContextVar("client_phone", default=None)
client_id_ctx: ContextVar[str | None] = ContextVar("client_id", default=None)
wa_message_id_ctx: ContextVar[str | None] = ContextVar("wa_message_id", default=None)
