# Project Specification: Headless CMS/Commerce Auth Refactor (2026 Edition)

## Context
Refactoring a legacy Python app to a high-security, Multi-Tenant Headless system.
**Tech Stack:** FastAPI, SQLAlchemy (Async), Pydantic V2, Zitadel (OIDC), Vue 3.

## Architectural Requirements

### 1. Identity & Config
*   **Provider Agnostic:** Uses OIDC Discovery (`.well-known/openid-configuration`). No hardcoded Zitadel URLs in code.
*   **Public Config:** Expose `GET /api/public/config` returning `{ authority: str, client_id: str }` for the frontend.
*   **Environment:** All secrets loaded via Pydantic Settings (`.env`).

### 2. The "Three-API" Strategy
*   **Super-Admin API:** Platform owners (create tenants).
*   **Backoffice API:** Tenant Staff. Supports **Multi-Org Users** (One user, multiple shops). Claims must be validated against the specific `org_id`.
*   **Storefront API:** End customers.

### 3. Strict Database Multi-Tenancy
*   **Pattern:** "Row-Level Security via Application Logic".
*   **Injection:** Do not trust Headers. Tenant ID comes from the Validated JWT.
*   **Dependency:** `get_tenant_db`. A FastAPI dependency that returns a helper or session wrapper that automatically appends `.where(tenant_id=current_tenant)` to every query.
*   **Audit Logging:** All Models must inherit a Mixin that automatically tracks `created_by_user_id` and `updated_by_user_id` from the context, and `created_at`/`updated_at`.

### 4. RBAC (Java-Style)
*   Implement a Dependency Factory: `RequirePermission("orders.read")`.
*   This must check Zitadel roles/grants inside the JWT.

### 5. Webhooks
*   Endpoint: `/api/webhooks/zitadel`
*   Purpose: Listen for `User.Locked`, `User.Deleted` to sync local DB state.

---

## Implementation Plan

**Step 1: Infrastructure**
*   `docker-compose.yml`: Add Zitadel (start fresh, isolated DB).
*   `config.py`: Pydantic settings.

**Step 2: Bootstrap Automation**
*   `setup_zitadel.py`: A Python script that:
    1. Waits for Zitadel to be healthy.
    2. Authenticates as Machine User.
    3. Creates default `Organization` and `Project`.
    4. Creates `OIDC Applications` (API & Frontend).
    5. Defines `Roles` (Admin, Editor).

**Step 3: Backend Core**
*   `auth.py`: OIDC/JWT verification and `get_current_user`.
*   `dependencies.py`: The `RequirePermission` factory and `get_tenant_db`.
*   `models.py`: SQLAlchemy Base with `TenantMixin` and `AuditMixin`.

**Step 4: API Routers**
*   Basic implementation of the 3 API sections using the dependencies above.

**Step 5: Frontend (Vue 3)**
*   Minimal "Context Switcher" app.
*   Login -> List User's Grants (Shops) -> Click Shop -> Silent Token Exchange for Org-Specific Token -> Call API.
