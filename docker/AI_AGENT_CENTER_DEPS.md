# AI Agent Center Server Dependencies

AI Agent Center uses RAG-Anything for document parsing and multimodal retrieval. The Python packages are declared in `pyproject.toml`; production servers or custom images also need system packages for Office/PDF parsing.

## Production Checklist

- Install this app with its Python dependencies during image build or deploy. `bench get-app /path/to/frappe-crm` should install the pinned packages from `pyproject.toml`.
- Keep the site `private/files` directory on a persistent volume. The native RAGAnything index is stored at `sites/<site>/private/files/ai_agent_center_rag` by default.
- Configure `FCRM Settings > AI Settings` before reindexing: provider `Kimi`, base URL `https://api.moonshot.ai/v1`, model `kimi-k2.6`, and a valid Moonshot API key.
- Run the post-deploy status check and reindex commands below after migrations.
- Size the worker/container for AI indexing. Use at least 4 GB RAM for demo data; 8 GB is safer for PDF/Excel parsing plus local embeddings.

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

## Docker Image Notes

If you build a custom Frappe image, add the Debian/Ubuntu packages above before `bench get-app` or app install. The Python dependencies pinned in `pyproject.toml` include:

- `raganything[all]`
- `lightrag-hku`
- `mineru`
- `sentence-transformers`

RAGAnything calls MinerU through the `mineru` CLI. The application prepends the current Python environment `bin` directory to `PATH`, so the CLI works in bench web, worker, scheduler, and `bench execute` processes as long as the package is installed in the same environment as Frappe.

## Runtime Settings

- Configure `FCRM Settings > AI Settings > Kimi API Key` or `Moonshot API Key`.
- Keep the API key server-side only.
- Default model: `kimi-k2.6`.
- Default local embedding model: `BAAI/bge-m3`.
- Default RAG storage: `private/files/ai_agent_center_rag`.

## Post-Deploy Commands

Run these commands inside the backend container after `bench migrate`:

```bash
bench --site <site-name> execute crm.api.ai_agent_center.get_rag_status
bench --site <site-name> execute crm.api.ai_agent_center.reindex_rag
bench --site <site-name> execute crm.api.ai_agent_center.get_rag_status
```

Expected healthy status:

```json
{
  "native_raganything_ready": true,
  "raganything_package_available": true,
  "mineru_package_available": true,
  "mineru_command_available": true,
  "mineru_parser_available": true,
  "status": "RAGAnything Ready"
}
```

If `mineru_command_available` is false, the app dependencies were not installed into the active bench Python environment. Reinstall the CRM app dependencies in the backend image/container, then rerun the status command.

If reindexing times out on Moonshot/Kimi, rerun it once after network/API latency settles. For demos, keep the first indexed dataset small and reindex before the presentation.
