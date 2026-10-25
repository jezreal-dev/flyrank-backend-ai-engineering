# AI Rematch Prompts & Evaluation (BE-03: Auth · Login & Protect)

## 1. Prompt Written From Memory (Stage 7 Exercise)
> "You are an expert backend engineer. Build a secure FastAPI authentication service using Supabase Auth as the Identity Provider (IdP).
> Requirements:
> 1. Store `SUPABASE_URL` and `SUPABASE_KEY` in `.env` (never hardcode credentials).
> 2. Implement the following endpoints:
>    - `POST /auth/signup`: Accepts email & password. Missing inputs return 400; success returns 201 with user object.
>    - `POST /auth/login`: Accepts credentials. Missing inputs return 400; invalid credentials return 401; success returns 200 with JWT access & refresh tokens.
>    - `POST /auth/logout`: Protected endpoint that invalidates session and returns 204 No Content.
>    - `GET /public/info`: Unprotected endpoint returning 200.
>    - `GET /protected/profile`: Guarded endpoint returning 200 with user metadata. Missing/invalid token returns 401.
>    - `GET /protected/dashboard`: Second protected endpoint demonstrating reusable auth middleware.
> 3. Token verification must be extracted into a reusable FastAPI dependency (`Depends()`) using `HTTPBearer` so Swagger UI (/docs) shows the Authorize padlock button.
> 4. Error responses must strictly follow the `{ "error": "..." }` JSON format."

---

## 2. Code Review Questions Answered
1. **How did the AI handle token extraction?**
   - Naive AI implementations often parse `request.headers.get("Authorization")` manually with split operations without validating the `"Bearer "` prefix or handling IndexError on malformed headers, causing 500 Internal Server Errors instead of clean 401 Unauthorized responses. Our implementation uses FastAPI's `HTTPBearer(auto_error=False)` combined with explicit header validation.
2. **What security flaws might it have introduced?**
   - The AI frequently attempts to use `supabase.auth.get_user(token)` but fails to catch network timeouts or malformed JWT errors, or inadvertently recommends using the high-privilege `service_role` key instead of the public `anon` key.
3. **What did the prompt forget to specify?**
   - The initial prompt didn't specify disabling Supabase's default "Confirm email" requirement for local test suites, which would have blocked instant logins.
