"""Testes unitários do Clipboard Integration Service."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sanitizer import DataSanitizer
from observer_event import ClipboardSubject, ClipboardObserver
from clipboard_manager import ClipboardManager


class TestSanitizer:
    def setup_method(self):
        self.s = DataSanitizer()

    def test_sanitize_cpf(self):
        res = self.s.sanitize("Meu CPF é 123.456.789-00 para cadastro")
        assert res["was_sanitized"] is True
        assert "000.000.000-00" in res["sanitized_text"]

    def test_sanitize_email(self):
        res = self.s.sanitize("Contato em joao.silva@empresa.com.br por favor")
        assert res["was_sanitized"] is True
        assert "user@example.com" in res["sanitized_text"]

    def test_sanitize_api_key(self):
        res = self.s.sanitize('api_key = "secret_token_12345678"')
        assert res["was_sanitized"] is True
        assert "TEST_TOKEN_API_KEY_001" in res["sanitized_text"]

    def test_clean_text_not_sanitized(self):
        res = self.s.sanitize("Texto totalmente limpo sem dados sensíveis.")
        assert res["was_sanitized"] is False
        assert res["replacements_count"] == 0


class DummyObserver(ClipboardObserver):
    def __init__(self):
        self.events = []

    def on_clipboard_change(self, event: dict):
        self.events.append(event)


class TestClipboardManager:
    def setup_method(self):
        self.cm = ClipboardManager()

    def test_set_and_get(self):
        res = self.cm.set_content("Texto simples de teste")
        assert res["status"] == "success"
        curr = self.cm.get_content()
        assert curr["content"] == "Texto simples de teste"

    def test_auto_sanitizes_on_set(self):
        res = self.cm.set_content("Meu email é teste@dominio.com")
        assert res["sanitized"] is True
        curr = self.cm.get_content()
        assert "user@example.com" in curr["content"]

    def test_observer_notification(self):
        obs = DummyObserver()
        self.cm.attach(obs)
        self.cm.set_content("Novo conteúdo")
        assert len(obs.events) == 1
        assert obs.events[0]["content"] == "Novo conteúdo"

    def test_history(self):
        self.cm.set_content("Item 1")
        self.cm.set_content("Item 2")
        hist = self.cm.get_history()
        assert len(hist) == 2
        assert hist[0]["content"] == "Item 2"

    def test_clear(self):
        self.cm.set_content("Teste")
        self.cm.clear()
        assert self.cm.get_content()["content"] == ""
        assert len(self.cm.get_history()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
