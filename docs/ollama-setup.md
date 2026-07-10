# Ollama Setup

AI is disabled by default.

```env
AI_PROVIDER=ollama
AI_ENABLED=false
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_FALLBACK_MODEL=llama3.2:3b
```

Optional local setup:

```powershell
ollama pull qwen2.5:7b-instruct
ollama run qwen2.5:7b-instruct
```

Then set:

```env
AI_ENABLED=true
```

Status:

```text
GET /api/ai/status
```

If Ollama is not running, the app uses deterministic fallback and continues to work.
