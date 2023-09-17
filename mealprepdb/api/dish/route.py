from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import dish as model, dish_ingredient as dish_ing_model
from aiodal.oqm import views
from aiodal import dal
from ..base import ObjectIdFromUrl
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

    q = model.DishListQ(where=params)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return model.DishListView.model_validate(data)


@router.get("/{id}")
async def dish_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishResource:
    """Return an dish detail."""

    detail_params = ObjectIdFromUrl(id)
    q = model.DishDetailQ(where=detail_params)
    data = await views.DetailViewQuery.from_query(transaction, q)

    return model.DishResource.model_validate(data.obj)


@router.get("/{id}/ingredients")
async def dish_ingredient_list_view(
    id: int,
    request: Request,
    params: dish_ing_model.DishIngredientQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> dish_ing_model.DishIngredientListView:
    """Return a list of ingredients used in a dish."""

    params_ = dish_ing_model.PrivateDishIngredientQueryParams(dish_id=id, params=params)
    q = dish_ing_model.DishIngredientListQ(where=params_)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return dish_ing_model.DishIngredientListView.model_validate(data)
