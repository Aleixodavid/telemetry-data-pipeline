"""
Observer Pattern — Sistema de Notificação de Eventos de Clipboard.

Permite registrar observadores para reagir a mudanças no clipboard
(ex: sanitização automática, logging, gatilhos de automação).
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("ObserverPattern")


class ClipboardObserver(ABC):
    """Interface abstrata para observadores de eventos de clipboard."""

    @abstractmethod
    def on_clipboard_change(self, event: dict):
        """Método invocado quando o conteúdo do clipboard muda."""
        pass


class ClipboardSubject:
    """Sujeito observável que notifica observadores registrados."""

    def __init__(self):
        self._observers = []

    def attach(self, observer: ClipboardObserver):
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"[Observer] Observador adicionado: {observer.__class__.__name__}")

    def detach(self, observer: ClipboardObserver):
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"[Observer] Observador removido: {observer.__class__.__name__}")

    def notify(self, event: dict):
        logger.debug(f"[Observer] Notificando {len(self._observers)} observadores...")
        for observer in self._observers:
            try:
                observer.on_clipboard_change(event)
            except Exception as e:
                logger.error(f"[Observer] Erro em {observer.__class__.__name__}: {e}")
