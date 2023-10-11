from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import (
    meal as model,
    meal_ingredient as meal_ing_model,
    meal_dish as meal_dish_model,
)
from aiodal import dal
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

    return await model.MealListView.get(
        transaction=transaction, request_url=str(request.url), params=params
    )


@meal_router.get("/{id}")
async def meal_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.MealResource:
    """Return an meal detail."""

    return await model.MealResource.detail(transaction, obj_id=id)


@meal_router.post("/")
async def meal_create_view(
    form: model.MealCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.MealResource:
    """Return an meal create."""

    return await model.MealResource.create(transaction, form=form)


@meal_router.put("/{id}")
async def meal_update_view(
    id: int,
    form: model.MealUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.MealResource:
    """Return an meal update."""

    return await model.MealResource.update(transaction, obj_id=id, form=form)


@ingredient_router.get("/{id}/meal/")
async def ingredient_meal_list_view(
    id: int,
    request: Request,
    params: meal_ing_model.MealIngredientQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_ing_model.MealIngredientListView:
    """Return a list of meal for an ingredient in inventory."""

    return await meal_ing_model.MealIngredientListView.from_ingredient(
        transaction=transaction,
        ingredient_id=id,
        request_url=str(request.url),
        params=params,
    )


@router.post("/meal_ingredient", tags=["meal_ingredient"])
async def meal_ingredient_create_view(
    form: meal_ing_model.MealIngredientCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_ing_model.MealIngredientResource:
    """Return a meal ingredient create."""

    return await meal_ing_model.MealIngredientResource.create(transaction, form=form)


@router.put("/meal_ingredient/{id}", tags=["meal_ingredient"])
async def meal_ingredient_update_view(
    id: int,
    form: meal_ing_model.MealIngredientUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_ing_model.MealIngredientResource:
    """Return a meal ingredient update."""

    return await meal_ing_model.MealIngredientResource.update(
        transaction, obj_id=id, form=form
    )


@dish_router.get("/{id}/meal/")
async def dish_meal_list_view(
    id: int,
    request: Request,
    params: meal_dish_model.MealDishQueryParams = Depends(),
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_dish_model.MealDishListView:
    """Return a list of meals consumed for a dish."""

    return await meal_dish_model.MealDishListView.from_dish(
        transaction=transaction,
        dish_id=id,
        request_url=str(request.url),
        params=params,
    )


@router.post("/meal_dish", tags=["meal_dish"])
async def meal_dish_create_view(
    form: meal_dish_model.MealDishCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_dish_model.MealDishResource:
    """Return a dish ingredient create."""

    return await meal_dish_model.MealDishResource.create(transaction, form=form)


@router.put("/meal_dish/{id}", tags=["meal_dish"])
async def meal_dish_update_view(
    id: int,
    form: meal_dish_model.MealDishUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> meal_dish_model.MealDishResource:
    """Return a dish ingredient update."""

    return await meal_dish_model.MealDishResource.update(
        transaction, obj_id=id, form=form
    )


router.include_router(meal_router)
router.include_router(dish_router)
router.include_router(ingredient_router)
