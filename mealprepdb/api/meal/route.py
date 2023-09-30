from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import (
    meal as model,
    meal_ingredient as meal_ing_model,
    meal_dish as meal_dish_model,
)
from aiodal.oqm import views
from aiodal import dal
from ..base import ObjectIdFromUrl
from typing import List, Any

deps: List[Any] = [
    # Depends(auth0.implicit_scheme),
]

router = APIRouter()

meal_router = APIRouter(prefix="/meal", tags=["meal"], dependencies=deps)
dish_router = APIRouter(prefix="/dish", tags=["dish"], dependencies=deps)
ingredient_router = APIRouter(
    prefix="/ingredient", tags=["ingredient"], dependencies=deps
)


@meal_router.get("/")
async def meal_list_view(
    request: Request,
    params: model.MealQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.MealListView:
    """Return a list of meals"""

    q = model.MealListQ(where=params)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return model.MealListView.model_validate(data)


@meal_router.get("/{id}")
async def meal_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.MealResource:
    """Return an meal detail."""

    detail_params = ObjectIdFromUrl(id)
    q = model.MealDetailQ(where=detail_params)
    data = await views.DetailViewQuery.from_query(transaction, q)

    return model.MealResource.model_validate(data.obj)


@ingredient_router.get("/{id}/meal/")
async def ingredient_meal_list_view(
    id: int,
    request: Request,
    params: meal_ing_model.MealIngredientQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_ing_model.MealIngredientListView:
    """Return a list of meal for an ingredient in inventory."""

    params_ = meal_ing_model.PrivateMealIngredientQueryParams(
        ingredient_id=id, params=params
    )
    q = meal_ing_model.MealIngredientListQ(where=params_)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return meal_ing_model.MealIngredientListView.model_validate(data)


@dish_router.get("/{id}/meal/")
async def dish_meal_list_view(
    id: int,
    request: Request,
    params: meal_dish_model.MealDishQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_dish_model.MealDishListView:
    """Return a list of meals consumed for a dish."""

    params_ = meal_dish_model.PrivateMealDishQueryParams(dish_id=id, params=params)
    q = meal_dish_model.MealDishListQ(where=params_)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return meal_dish_model.MealDishListView.model_validate(data)


router.include_router(meal_router)
router.include_router(dish_router)
router.include_router(ingredient_router)
