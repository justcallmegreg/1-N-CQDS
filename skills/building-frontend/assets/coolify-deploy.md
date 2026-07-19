# Preview deploy — Coolify

Coolify hosts the frontend mock at a shareable URL so stakeholders can click it
before backends exist. You run your own Coolify instance; this documents the deploy.

## One-time
1. In Coolify, create a project and add a **Static Site** (or **Nixpacks**) resource
   pointing at this repo, build path `frontend/`.
2. Build command `npm run build`, output dir `dist/` (Vite) or `.output/`/`out/`
   (Next/Astro adapter).
3. Set a domain; Coolify provisions TLS.

## Each preview
- Push the branch; Coolify auto-deploys (if you enabled it) or click **Deploy**.
- Share the URL. This is a MOCK — it need not have live backends; stub data is fine.

## Not in scope here
This plan does not push to a Coolify instance (no assumed instance/credentials).
Dev-time verification uses Playwright locally. When you have Coolify, this is the deploy path.
