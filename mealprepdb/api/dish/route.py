from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import dish as model, dish_ingredient as dish_ing_model
from aiodal import dal
from typing import List, Any

deps: List[Any] = [
    # Depends(auth0.implicit_scheme),
]
router = APIRouter(prefix="/dish", tags=["dish"], dependencies=deps)


@router.get("/")
async def dish_list_view(
    request: Request,
    params: model.DishQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishListView:
    """Return a list of dishes"""

    return await model.DishListView.get(
        transaction=transaction, request_url=str(request.url), params=params
    )


@router.get("/{id}")
async def dish_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishResource:
    """Return an dish detail."""

    return await model.DishResource.detail(transaction, obj_id=id)


@router.get("/{id}/ingredient/")
async def dish_ingredient_list_view(
    id: int,
    request: Request,
    params: dish_ing_model.DishIngredientQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> dish_ing_model.DishIngredientListView:
    """Return a list of ingredients used in a dish."""

    return await dish_ing_model.DishIngredientListView.from_dish(
        transaction=transaction, dish_id=id, request_url=str(request.url), params=params
    )
