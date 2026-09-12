"""
Clipboard Integration Service — Microsserviço da Área de Transferência
Arquitetura: Observer Pattern para notificação em tempo real + Sanitizador de dados sensíveis.

Credenciais de demonstração: admin / admin
"""

import os
import json
import logging
from flask import Flask, request, jsonify

from clipboard_manager import ClipboardManager
from sanitizer import DataSanitizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logger = logging.getLogger("ClipboardService")

app = Flask(__name__)
app.secret_key = config.get("secret_key", "clipboard_demo_secret")

clipboard = ClipboardManager(max_history=config.get("max_history", 50))
sanitizer = DataSanitizer()


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == "admin" and auth.password == "admin":
            return f(*args, **kwargs)
        data = request.get_json(silent=True) or {}
        if data.get("username") == "admin" and data.get("password") == "admin":
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated


@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "service": "Clipboard Integration Service",
        "version": "1.0.0",
        "history_count": len(clipboard.get_history()),
    })


@app.route("/api/clipboard", methods=["GET"])
@require_auth
def get_clipboard():
    """Obtém o conteúdo atual da área de transferência."""
    return jsonify(clipboard.get_content())


@app.route("/api/clipboard", methods=["POST"])
@require_auth
def set_clipboard():
    """Define novo conteúdo na área de transferência (com sanitização automática)."""
    data = request.get_json(silent=True) or {}
    text = data.get("content", "")
    source = data.get("source", "api_request")

    if not text:
        return jsonify({"error": "Field 'content' is required"}), 400

    result = clipboard.set_content(text, source)
    return jsonify(result)


@app.route("/api/clipboard/history")
@require_auth
def get_history():
    """Retorna o histórico de entradas no clipboard."""
    limit = min(int(request.args.get("limit", 20)), 50)
    return jsonify({"history": clipboard.get_history(limit)})


@app.route("/api/clipboard/clear", methods=["POST"])
@require_auth
def clear_clipboard():
    """Limpa a área de transferência e histórico."""
    clipboard.clear()
    return jsonify({"status": "cleared"})


@app.route("/api/sanitize", methods=["POST"])
@require_auth
def test_sanitize():
    """Testa o motor de sanitização sem alterar a área de transferência."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    return jsonify(sanitizer.sanitize(text))


if __name__ == "__main__":
    print("=" * 60)
    print("  Clipboard Integration Service — Observer & Sanitizer")
    print("  Credenciais: admin / admin")
    print("  Endpoint: http://127.0.0.1:5004")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5004, debug=False)
