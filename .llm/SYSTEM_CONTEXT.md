# Project Context: OSS Headless CMS & Ecommerce (Codename: Onyx)
**Date Context:** December 2025
**Philosophy:** FOSS, Modular, Performance, Designer-Friendly.

## Tech Stack
- **Backend:** Python 3.14+, FastAPI, Pydantic v2 (Strict), SQLAlchemy (Async), Alembic.
- **Auth:** Zitadel v4 (OIDC/OAuth2). No local password storage.
- **Database:** PostgreSQL 18 (Multi-tenant via Schemas or RLS).
- **Queue/Async:** RabbitMQ + FastStream / Temporal.io for workflows.
- **Cache:** Valkey (Redis FOSS fork).
- **Proxy:** Traefik v3 (Auto SSL).
- **Frontend (Admin):** Nuxt 4, TailwindCSS v4, Pinia, Shadcn-vue.
- **SDK:** TypeScript, Fetch API (Isomorphic).
- **Workflow Engine:** Temporal. Will changed later

## Core Architectural Rules
1.  **Multi-Tenancy:** The system is single-installation, multi-tenant. Every DB query must filter by `tenant_id` or use Postgres schemas scoped to the tenant.
2.  **API Separation:**
    - `/api/v1/management`: Protected by JWT (Zitadel). For Admin/Staff. (Read/Write everything).
    - `/api/v1/storefront`: Public (or Public Key). Cached heavily. Read-only mostly, except Cart/Checkout.
3.  **Workflow First:** Do not hardcode "Send Email after Order". Instead, emit an Event `ORDER_CREATED`. The Workflow Engine picks it up.
4.  **The "Shopify" Editor:** API responses include `blocks` and `sections` JSON. The frontend renders these dynamically.
5.  **Monorepo:** Use relative imports within packages.

## Coding Standards (Dec 2025)
- **Python:** Fully Async (`async def`). Type hints are mandatory (`def fn() -> str:`). Use `uv` for dependency management.
- **Documentation:** Every API endpoint must have a Swagger/OpenAPI description + Pydantic Example.
- **Error Handling:** Centralized Exception handlers returning standardized JSON errors.
