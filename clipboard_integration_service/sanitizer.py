"""
Sanitizer Engine — Sanitização automática de dados sensíveis em textos.
Remove/mascara CPFs, cartões de crédito, API keys, tokens JWT e e-mails.
"""

import re
import logging

logger = logging.getLogger("Sanitizer")


class DataSanitizer:
    """Mecanismo de sanitização baseado em regex de segurança."""

    PATTERNS = [
        # API Keys e Tokens (ex: TEST_TOKEN_API_KEY_001, sk-..., ghp_...)
        (r'(?i)(api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{8,})["\']?',
         r'\1: "TEST_TOKEN_API_KEY_001"'),

        # Cartão de crédito (16 dígitos)
        (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[REDACTED_CREDIT_CARD]'),

        # CPF (xxx.xxx.xxx-xx ou 11 dígitos)
        (r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '000.000.000-00'),

        # Email
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'user@example.com'),

        # Tokens JWT (eyJ...)
        (r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'TEST_TOKEN_JWT_PLACEHOLDER'),
    ]

    def sanitize(self, text: str) -> dict:
        """
        Sanitiza o texto fornecido, substituindo padrões sensíveis.

        Returns:
            {"original_length": int, "sanitized_text": str, "was_sanitized": bool, "replacements_count": int}
        """
        if not text or not isinstance(text, str):
            return {"original_length": 0, "sanitized_text": "", "was_sanitized": False, "replacements_count": 0}

        sanitized = text
        replacements = 0

        for pattern, replacement in self.PATTERNS:
            new_text, count = re.subn(pattern, replacement, sanitized)
            if count > 0:
                replacements += count
                sanitized = new_text

        was_sanitized = replacements > 0
        if was_sanitized:
            logger.info(f"[Sanitizer] {replacements} substituição(ões) de dados sensíveis efetuada(s).")

        return {
            "original_length": len(text),
            "sanitized_text": sanitized,
            "was_sanitized": was_sanitized,
            "replacements_count": replacements,
        }
