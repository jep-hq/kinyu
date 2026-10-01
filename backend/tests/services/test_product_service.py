import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.catalog_service import ProductService
from app.schemas.catalog import ProductVariantCreate
from app.models.ecommerce import Product

@pytest.mark.asyncio
async def test_add_variant_to_product():
    # Setup
    mock_session = AsyncMock()
    # Ensure session.add is a standard Mock, NOT an AsyncMock, because it's called synchronously
    mock_session.add = MagicMock()

    service = ProductService(mock_session, tenant_id=uuid4())

    product_id = uuid4()
    mock_product = Product(id=product_id, title="Test Product", tenant_id=service.repository.tenant_id)

    # Mock repository.get to return product
    service.repository.get = AsyncMock(return_value=mock_product)

    # Mock get_with_variants to return the product
    service.get_with_variants = AsyncMock(return_value=mock_product)

    variant_in = ProductVariantCreate(title="New Variant", price=100)

    # Execute
    result = await service.add_variant(product_id, variant_in)

    # Assert
    assert result == mock_product
    service.repository.get.assert_called_once_with(product_id)

    # Verify session interactions
    assert mock_session.add.called
    assert mock_session.commit.called
    # It refreshes the product, not the variant usually in the code I wrote logic:
    # await self.repository.session.refresh(product)
    # Actually wait, in my implementation:
    # return await self.get_with_variants(product_id)
    # And before that I did:
    # await self.repository.session.refresh(product) (No, I wrote refresh(product)?)

    # Let's check my implementation of add_variant again:
    # await self.repository.session.refresh(product) <- No, I can't refresh if I didn't verify it was attached.
    # Wait, fetching it with `get` attaches it to session usually if using ORM.

    # In strict unit test with mocks, we just verify methods are called.
