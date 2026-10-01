import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4, UUID
from unittest.mock import patch, AsyncMock
from app.main import app
from app.api import deps
from app.core.auth_zitadel import ZitadelUser

@pytest.mark.asyncio
async def test_create_product_variant_endpoint():
    # Mock User and Tenant
    tenant_id = uuid4()
    mock_user = ZitadelUser(
        sub="test-user",
        org_id=str(tenant_id),
        project_roles=["admin"],
        username="testuser"
    )

    async def mock_get_current_user():
        return mock_user

    async def mock_get_tenant_id():
        return tenant_id

    app.dependency_overrides[deps.get_current_user] = mock_get_current_user
    app.dependency_overrides[deps.get_tenant_id] = mock_get_tenant_id
    # Use lambda to allow FastAPI to inspect signature correctly (no args)
    # properly mocking the AsyncGenerator that get_session is
    app.dependency_overrides[deps.get_session] = lambda: AsyncMock()

    product_id = uuid4()

    # Mock behavior of ProductService.add_variant
    # Since endpoint calls: product = await service.add_variant(id, variant_in)
    # We return a dict or object matching ProductResponse

    mock_product_data = {
        "id": product_id,
        "title": "Test Product",
        "handle": "test-product",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "variants": [
            {
                "id": uuid4(),
                "product_id": product_id,
                "title": "New Variant",
                "price": 100.0,
                "inventory_quantity": 0,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        ]
    }

    with patch("app.services.catalog_service.ProductService.add_variant", new_callable=AsyncMock) as mock_add_variant:
        mock_add_variant.return_value = mock_product_data

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                f"/api/v1/products/{product_id}/variants",
                json={"title": "New Variant", "price": 100}
            )

        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["title"] == "Test Product"
        assert len(data["variants"]) == 1
        assert data["variants"][0]["title"] == "New Variant"

        mock_add_variant.assert_called_once()

    # Clean up
    app.dependency_overrides = {}
