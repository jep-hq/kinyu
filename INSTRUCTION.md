
# The Prompt

**Role:** Act as a Senior Principal Software Architect and Lead Full Stack Developer. You are an expert in "State of the Art" 2026 web development standards.

**Goal:** Create the architectural blueprint, database schema, and core scaffolding for a high-performance **Headless E-commerce & CMS System**.

**Tech Stack Requirements:**
*   **Backend:** Python (FastAPI), Pydantic V2, SQLModel (or Async SQLAlchemy 2.0), Alembic (Migrations), Swagger/Redoc.
*   **Database:** PostgreSQL (with JSONB support for dynamic CMS content).
*   **Frontend:** Nuxt 4 (or latest Nuxt 3), TypeScript, Pinia (Store), TailwindCSS, implementation of a "Dynamic Page Builder" pattern.
*   **Services:** Mollie (Payments), SMTP/SendGrid (Transactional Emails).
*   **Standards (2026):** Fully typed (Strict Mode), Async/Await everywhere, RBAC (Role Based Access Control), JWT + Refresh Tokens inside HttpOnly cookies, Dockerized, CI/CD ready structure.

**Task 1: The "Shopify-Grade" Data Model**
I need a strict, relational database schema that mimics Shopify's object density but retains Headless CMS flexibility. Define the Python (SQLModel/SQLAlchemy) models for the following domains. Use Mixins for common fields (UUIDs, timestamps).

1.  **Auth & System:**
    *   `Users` (Admin/Staff), `Roles`, `Permissions` (Granular RBAC).
2.  **CMS (Headless):**
    *   `ContentModel` (Defines the shape of data - like Strapi).
    *   `ContentEntry` (The actual data).
    *   `MediaLibrary` (Images/Videos with metadata).
    *   `Navigation` (Nested menus).
    *   `SEO` (Polymorphic mixin applied to products, pages, categories).
3.  **E-commerce (Shopify Parity):**
    *   `Collections` (Smart & Manual categories).
    *   `Products` (Base info).
    *   `ProductVariants` (SKU, Price, Inventory Management, Options like Size/Color).
    *   `Customers` (Auth, Saved Addresses, Marketing preferences).
    *   `Cart` & `CartItems` (Persistent Redis-backed or DB-backed).
    *   `Orders` (Status, Payment Status, Fulfillment Status).
    *   `LineItems` (Snapshot of product data at time of purchase).
    *   `Discounts` (Rule-based engine).
    *   `Taxes` & `ShippingRates`.
4.  **Payments (Mollie Integration):**
    *   `Transactions` (Mollie ID, Method, Status, Webhook logs).

**Task 2: Backend Core Implementation (FastAPI)**
Provide the folder structure and the base setup for:
1.  `main.py` with lifespan events and CORS.
2.  A generic `Service` and `Repository` pattern class to handle CRUD operations dynamically (so I don't write generic CRUD 50 times).
3.  The **Mollie Webhook Handler** endpoint (securely verifying signatures).
4.  The **Email Service** dependency injection setup.

**Task 3: Frontend Core Implementation (Nuxt)**
1.  Provide the `composables/useFetchAPI.ts` (Interceptor based wrapper for $fetch).
2.  Desribe the **Dynamic Page Builder** component logic: How to map a JSON response from the CMS (e.g., `type: 'hero-slider'`) to a Vue component `<HeroSlider />` dynamically without massive if/else chains.

**Constraint:**
Do not assume simple MVP code. Write code that handles errors, types, and environment variables. Assuming we are in 2026, prioritize performance and security.
