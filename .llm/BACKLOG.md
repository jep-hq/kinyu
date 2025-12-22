# Development Backlog

## Epic 1: Infrastructure & Auth Foundation
- [ ] **Task 1.1:** Setup `docker-compose.yml` with Traefik, PostgreSQL, Valkey, Zitadel, and RabbitMQ. Ensure networking allows internal communication.
- [ ] **Task 1.2:** Initialize FastAPI Monorepo structure using `uv`. Configure SQLAlchemy 2.0 Async engine.
- [ ] **Task 1.3:** Implement **Multi-tenant Middleware**. Extract `X-Tenant-ID` from headers or domain mapping.
- [ ] **Task 1.4:** Integrate Zitadel. Create a dependency `get_current_user` that validates JWTs against Zitadel's JWKS.

## Epic 2: Core Data Modeling (The "Objects")
- [ ] **Task 2.1:** Create `Product` model. Needs: UUID, slug, translatable title/desc, `b2b_settings` (dict), `subscription_plan` (relation).
- [ ] **Task 2.2:** Create **Variant System**. `ProductVariant` table. Needs: SKU, Price, Stock, `attributes` (JSONB for generic key-values e.g., Color=Red).
- [ ] **Task 2.3:** Create `PriceList` system. A Variant has a base price. `PriceListOverride` table maps `Variant + CustomerGroup -> Price`.
- [ ] **Task 2.4:** Migration Script generation for the above.

## Epic 3: The API Layer (Separation of Concerns)
- [ ] **Task 3.1:** Setup `/management` router. generic CRUD endpoints for Products (using Pydantic schemas).
- [ ] **Task 3.2:** Setup `/storefront` router. Read-only endpoints. Implement **Cache-Control** headers and Valkey caching layer for these routes.

## Epic 4: Workflow Engine (The "n8n" Replacement)
- [ ] **Task 4.1:** Setup **Temporal** or **FastStream** worker structure in `apps/worker-engine`.
- [ ] **Task 4.2:** Create an Event Bus. When `Product` is created, emit `event.product.created` to RabbitMQ.
- [ ] **Task 4.3:** Create a Workflow Definition: "On Order Placed". Steps: 1. Deduct Stock, 2. Calc Taxes, 3. Email Customer.

## Epic 5: The "Shopify-like" Page Builder
- [ ] **Task 5.1:** Design JSON Schema for Pages. Fields: `layout` (string), `sections` (List of Objects).
- [ ] **Task 5.2:** Create API for `Page` and `Block` management.
- [ ] **Task 5.3:** (Frontend) Create a Dynamic Component Renderer in Nuxt. `<RenderSection :data="section" />`.

## Epic 6: E-commerce Checkout & Payments
- [ ] **Task 6.1:** Cart Logic (Server-side). Redis-backed carts.
- [ ] **Task 6.2:** Mollie Integration. Create Payment Intent -> Redirect URL -> Webhook Handler.

## Epic 7: Admin Frontend (Nuxt)
- [ ] **Task 7.1:** Setup Nuxt 4 + Tailwind. Connect to Zitadel Login.
- [ ] **Task 7.2:** Build generic "Data Table" component with sorting/pagination.
- [ ] **Task 7.3:** Build the "Visual Editor" wrapper. Iframe or overlay to edit page blocks.
