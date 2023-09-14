from fastapi import APIRouter, Depends, Request

# from ..auth import auth0
from ..deps import get_transaction
from . import ingredient as model
from aiodal.oqm import views
from aiodal import dal
from ..base import ObjectIdFromUrl
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

    q = model.IngredientListQ(where=params)
    data = await views.TotalCountListViewQuery.from_query(
        transaction, request.url._url, params.offset, params.limit, q, "/v1"
    )

    return model.IngredientListView.model_validate(data)


@router.get("/{id}")
async def ingredient_detail_view(
    id: int,
    transaction: dal.TransactionManager = Depends(get_transaction),
    # _: Auth0User = Security(auth0.get_user, scopes=[READ_INGREDIENT]),
) -> model.IngredientResource:
    """Return an ingredient detail."""

    detail_params = ObjectIdFromUrl(id)
    q = model.IngredientDetailQ(where=detail_params)
    data = await views.DetailViewQuery.from_query(transaction, q)

    return model.IngredientResource.model_validate(data.obj)
