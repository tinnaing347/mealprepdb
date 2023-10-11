from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import dish as model, dish_ingredient as dish_ing_model
from aiodal import dal
from typing import List, Any

deps: List[Any] = [
    # Depends(auth0.implicit_scheme),
]
router = APIRouter()
dish_router = APIRouter(prefix="/dish", tags=["dish"], dependencies=deps)


@dish_router.get("/")
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


@dish_router.get("/{id}")
async def dish_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishResource:
    """Return an dish detail."""

    return await model.DishResource.detail(transaction, obj_id=id)


@dish_router.post("/")
async def dish_create_view(
    form: model.DishCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishResource:
    """Return an dish create."""

    return await model.DishResource.create(transaction, form=form)


@dish_router.put("/{id}")
async def dish_update_view(
    id: int,
    form: model.DishUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.DishResource:
    """Return an dish update."""

    return await model.DishResource.update(transaction, obj_id=id, form=form)


@dish_router.get("/{id}/ingredient/")
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


@router.post("/dish_ingredient", tags=["dish_ingredient"])
async def dish_ingredient_create_view(
    form: dish_ing_model.DishIngredientCreateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> dish_ing_model.DishIngredientResource:
    """Return an dish create."""

    return await dish_ing_model.DishIngredientResource.create(transaction, form=form)


@router.put("/dish_ingredient/{id}/", tags=["dish_ingredient"])
async def dish_ingredient_update_view(
    id: int,
    form: dish_ing_model.DishIngredientUpdateForm,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> dish_ing_model.DishIngredientResource:
    """Return an dish update."""

    return await dish_ing_model.DishIngredientResource.update(
        transaction, obj_id=id, form=form
    )


router.include_router(dish_router)
