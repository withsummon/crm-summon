# AI Agent Center Server Dependencies

AI Agent Center uses RAG-Anything for document parsing and multimodal retrieval. The Python packages are declared in `pyproject.toml`; production servers or custom images also need system packages for Office/PDF parsing.

## Debian / Ubuntu

```bash
apt-get update
apt-get install -y --no-install-recommends \
  libreoffice \
  poppler-utils \
  tesseract-ocr \
  tesseract-ocr-eng \
  tesseract-ocr-ind \
  libgl1 \
  libglib2.0-0
```

## Runtime Settings

- Configure `FCRM Settings > AI Settings > Kimi API Key` or `Moonshot API Key`.
- Keep the API key server-side only.
- Default model: `kimi-k2.6`.
- Default local embedding model: `BAAI/bge-m3`.
- Default RAG storage: `private/files/ai_agent_center_rag`.
