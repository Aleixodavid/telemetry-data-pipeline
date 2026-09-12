"""
Clipboard Manager — Gerenciador de área de transferência simulada / nativa.
Thread-safe, com suporte a histórico, sanitização automática e Observer Pattern.
"""

import time
import threading
import logging
from observer_event import ClipboardSubject, ClipboardObserver
from sanitizer import DataSanitizer

logger = logging.getLogger("ClipboardManager")


class AuditLogObserver(ClipboardObserver):
    """Observador que registra logs de auditoria para cada mudança de clipboard."""

    def __init__(self):
        self.log_history = []

    def on_clipboard_change(self, event: dict):
        record = {
            "timestamp": time.time(),
            "event_type": event.get("type", "content_changed"),
            "content_length": len(event.get("content", "")),
            "was_sanitized": event.get("was_sanitized", False),
        }
        self.log_history.append(record)
        logger.info(f"[AuditObserver] Mudança registrada: {record['content_length']} chars | Sanitizado: {record['was_sanitized']}")


class AutoSanitizerObserver(ClipboardObserver):
    """Observador que aciona a sanitização automática de conteúdo."""

    def __init__(self, sanitizer: DataSanitizer):
        self.sanitizer = sanitizer
        self.last_sanitized_result = None

    def on_clipboard_change(self, event: dict):
        raw_content = event.get("content", "")
        self.last_sanitized_result = self.sanitizer.sanitize(raw_content)


class ClipboardManager(ClipboardSubject):
    """
    Gerenciador principal da Área de Transferência.
    Permite leitura, escrita, histórico e notificação de observadores.
    """

    def __init__(self, max_history: int = 50):
        super().__init__()
        self.max_history = max_history
        self._current_content = ""
        self._history = []
        self._lock = threading.Lock()
        self.sanitizer = DataSanitizer()

        # Observadores padrão
        self.audit_observer = AuditLogObserver()
        self.sanitizer_observer = AutoSanitizerObserver(self.sanitizer)

        self.attach(self.audit_observer)
        self.attach(self.sanitizer_observer)

    def set_content(self, text: str, source: str = "user_input") -> dict:
        """
        Define o conteúdo da área de transferência com sanitização automática.
        """
        with self._lock:
            sanitization_result = self.sanitizer.sanitize(text)
            final_content = sanitization_result["sanitized_text"]

            self._current_content = final_content

            entry = {
                "id": len(self._history) + 1,
                "content": final_content,
                "original_text": "[REDACTED]" if sanitization_result["was_sanitized"] else text,
                "was_sanitized": sanitization_result["was_sanitized"],
                "source": source,
                "timestamp": time.time(),
            }

            self._history.insert(0, entry)
            if len(self._history) > self.max_history:
                self._history.pop()

        # Notificar observadores fora do lock
        event = {
            "type": "content_changed",
            "content": final_content,
            "was_sanitized": sanitization_result["was_sanitized"],
            "source": source,
        }
        self.notify(event)

        return {
            "status": "success",
            "sanitized": sanitization_result["was_sanitized"],
            "replacements": sanitization_result["replacements_count"],
            "content": final_content,
        }

    def get_content(self) -> dict:
        """Retorna o conteúdo atual da área de transferência."""
        with self._lock:
            return {
                "content": self._current_content,
                "length": len(self._current_content),
                "timestamp": time.time(),
            }

    def get_history(self, limit: int = 20) -> list:
        """Retorna o histórico recente de entradas no clipboard."""
        with self._lock:
            return self._history[:limit]

    def clear(self):
        """Limpa o conteúdo atual e o histórico."""
        with self._lock:
            self._current_content = ""
            self._history.clear()

        self.notify({"type": "cleared", "content": "", "was_sanitized": False, "source": "system"})
