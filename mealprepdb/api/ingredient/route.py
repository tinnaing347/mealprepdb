from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import ingredient as model, ingredient_in_inventory as inventory_model
from aiodal import dal
from typing import List, Any

deps: List[Any] = [
    # Depends(auth0.implicit_scheme),
]
router = APIRouter(prefix="/ingredient", tags=["ingredient"], dependencies=deps)


@router.get("/")
async def ingredient_list_view(
    request: Request,
    params: model.IngredientQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.IngredientListView:
    """Return a list of ingredients"""

    return await model.IngredientListView.get(
        transaction=transaction, request_url=str(request.url), params=params
    )


@router.get("/{id}")
async def ingredient_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.IngredientResource:
    """Return an ingredient detail."""

    return await model.IngredientResource.detail(transaction=transaction, obj_id=id)


@router.post("/")
async def ingredient_create_view(
    form: model.IngredientCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.IngredientResource:
    """Return an ingredient create."""

    return await model.IngredientResource.create(transaction, form=form)


@router.put("/{id}")
async def ingredient_update_view(
    id: int,
    form: model.IngredientUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.IngredientResource:
    """Return an ingredient update."""

    return await model.IngredientResource.update(transaction, obj_id=id, form=form)


@router.get("/inventory/")
async def ingredient_in_inventory_list_view(
    request: Request,
    params: inventory_model.IngredientInInventoryQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> inventory_model.IngredientInInventoryListView:
    """Return a list of ingredients in inventory"""

    return await inventory_model.IngredientInInventoryListView.get(
        transaction=transaction, request_url=str(request.url), params=params
    )


@router.get("/inventory/{id}")
async def ingredient_in_inventory_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> inventory_model.IngredientInInventoryResource:
    """Return an ingredient in inventory detail."""
    return await inventory_model.IngredientInInventoryResource.detail(
        transaction, obj_id=id
    )


@router.post("/inventory")
async def ingredient_in_inventory_create_view(
    form: inventory_model.IngredientInInventoryCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> inventory_model.IngredientInInventoryResource:
    """Return an ingredient create."""

    return await inventory_model.IngredientInInventoryResource.create(
        transaction, form=form
    )


@router.put("/inventory/{id}")
async def ingredient_in_inventory_update_view(
    id: int,
    form: inventory_model.IngredientInInventoryUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> inventory_model.IngredientInInventoryResource:
    """Return an ingredient update."""

    return await inventory_model.IngredientInInventoryResource.update(
        transaction, obj_id=id, form=form
    )
