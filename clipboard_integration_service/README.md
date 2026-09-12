# 📋 Clipboard Integration Service

> **Microsserviço de Integração de Área de Transferência & Sanitização de Dados Sensíveis**  
> Componente reativo para monitoramento da área de transferência, notificação orientada a eventos e proteção contra vazamento de credenciais.

---

## 🎯 Objetivo do Subprograma

O **Clipboard Integration Service** gerencia a interatividade com a área de transferência do sistema em ambientes corporativos e de automação. Seu foco principal é aplicar um **motor automatizado de redação e sanitização de dados sensíveis** antes que conteúdos copiados sejam armazenados, persistidos ou transmitidos para APIs externas.

---

## 🏛️ Arquitetura & Padrões de Projeto (*Design Patterns*)

### 1. **Observer Pattern (ClipboardSubject & ClipboardObserver)**
- **Arquivos:** `observer_event.py` / `clipboard_manager.py`
- **Funcionamento:** Quando o conteúdo da área de transferência é alterado, o gerenciador (*Subject*) dispara notificações automáticas para todos os observadores cadastrados (*Observers*):
  - `AuditLogObserver`: Registra logs de auditoria detalhados com contagem de caracteres e flags de segurança.
  - `AutoSanitizerObserver`: Aciona preventivamente o motor de sanitização de dados.

### 2. **Motor Sanitizador por Expressão Regular (Data Sanitizer Engine)**
- **Arquivo:** `sanitizer.py`
- **Padrões Detectados & Substituídos:**
  - **Tokens & API Keys:** Substituídos por `"TEST_TOKEN_API_KEY_001"`.
  - **Cartões de Crédito (16 dígitos):** Redigidos para `[REDACTED_CREDIT_CARD]`.
  - **CPFs Pessoais (`xxx.xxx.xxx-xx`):** Mascarados para `000.000.000-00`.
  - **Endereços de E-mail:** Substituídos por `user@example.com`.
  - **Tokens JWT (`eyJ...`):** Substituídos por `TEST_TOKEN_JWT_PLACEHOLDER`.

### 3. **Gerenciador de Estado Thread-Safe**
- **Arquivo:** `clipboard_manager.py`
- **Funcionamento:** Utiliza trava de exclusão mútua (`threading.Lock`) para garantir a integridade do histórico de transferências em aplicações concorrentes de alta frequência.

---

## 🔒 Sanitização & Segurança

- **Proteção Ativa:** Impede o vazamento inadvertido de chaves privadas, senhas ou dados pessoais (LGPD/GDPR) via clipboard.
- **Configuração Sanitizada:** Contém identificadores fictícios de demonstração (`TEST_TOKEN_API_KEY_001`, `TEST_CLIENT_SAMPLE_ID`).
- **Autenticação de Acesso:** Protegida por HTTP Basic Auth (`admin` / `admin`).

---

## 📡 Endpoints da API (Porta `5004`)

### `GET /api/clipboard`
Retorna o conteúdo atual armazenado na área de transferência (já sanitizado).

### `POST /api/clipboard`
Define novo conteúdo na área de transferência. O texto passa pelo filtro sanitizador antes de ser registrado no histórico e notificado aos observadores.
- **Body Exemplo:**
  ```json
  {
    "content": "Secret Token: api_key = 'sk_live_9988776655443322'",
    "source": "user_copy"
  }
  ```
- **Resposta Exemplo:**
  ```json
  {
    "content": "Secret Token: api_key: \"TEST_TOKEN_API_KEY_001\"",
    "replacements": 1,
    "sanitized": true,
    "status": "success"
  }
  ```

### `GET /api/clipboard/history`
Retorna a lista das últimas entradas registradas na área de transferência.

### `POST /api/clipboard/clear`
Limpa imediatamente o conteúdo atual e apaga o histórico de transferências.

### `POST /api/sanitize`
Permite testar o motor sanitizador com um texto arbitrário sem modificar a área de transferência.

---

## 🧪 Testes Unitários

Para executar os testes do Serviço de Clipboard:

```bash
cd D:\Pessoal\portifolio\clipboard_integration_service
python -m pytest tests/ -v
```
