# Deployment

Deployment configs are included, but actual deployment requires access to the user's Render, Vercel, and Supabase accounts.

## Backend on Render

1. Create a Render web service from this repository.
2. Set root directory to `backend`.
3. Use build command:

```bash
pip install -r requirements.txt
```

4. Use start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Optional environment variables:

```text
OLLAMA_URL=
OLLAMA_MODEL=llama3.1
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

## Frontend on Vercel

1. Set project root to `frontend`.
2. Set environment variable:

```text
VITE_API_URL=https://your-render-service.onrender.com
```

3. Build command:

```bash
pnpm run build
```

4. Output directory:

```text
dist
```

## Supabase Table

Run the SQL in `docs/SUPABASE_SCHEMA.sql`, then set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in Render.

## Current Readiness

- GitHub Actions CI is configured for backend and frontend.
- `render.yaml` is ready for Render.
- `frontend/vercel.json` is ready for Vercel.
- `docs/SUPABASE_SCHEMA.sql` is ready for Supabase.
- Account-specific deployment must be completed after logging into those services.

## Ollama Summary Layer

For local demos, run:

```bash
ollama pull llama3.1
ollama serve
```

Then set `OLLAMA_URL=http://localhost:11434`. If Ollama is not available, the backend uses a deterministic plain-English summary.
