from typing import Dict, Optional, Any, List
import dataclasses
from ..base import (
    Paginateable,
    BaseListViewQueryParamsModel,
    ListViewModel,
    ObjectIdFromUrl,
    ResourceUri,
    ParentResourceModel,
)
from aiodal import dal
from aiodal.oqm import dbentity, query
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query
import pydantic
import datetime
from .. import paginator


class DishIngredientQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        ingredient_name__contains: str = Query(None),
        ingredient_name: str = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.ingredient_name__contains = ingredient_name__contains
        self.ingredient_name = ingredient_name
        self.offset = offset
        self.limit = limit


class DishIngredientResource(ParentResourceModel):
    id: int
    dish_id: int
    dish_name: str
    ingredient_id: int
    ingredient_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    used_on: Optional[datetime.date] = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "dish": self._fastapi.url_path_for("dish_detail_view", id=self.dish_id),
                "ingredient_in_inventory": self._fastapi.url_path_for(
                    "ingredient_in_inventory_detail_view", id=self.ingredient_id
                ),
            }
        return None


class DishIngredientListView(ListViewModel[DishIngredientResource]):
    results: List[DishIngredientResource]

    @classmethod
    async def from_dish(
        cls,
        transaction: dal.TransactionManager,
        dish_id: int,
        request_url: str,
        params: DishIngredientQueryParams,
    ) -> "DishIngredientListView":
        t = transaction.get_table("dish_ingredient")
        dish = transaction.get_table("dish")
        ingredient = transaction.get_table("ingredient")
        ingredient_in_inventory = transaction.get_table("ingredient_in_inventory")
        stmt = (
            sa.select(
                t.c.id,
                t.c.dish_id,
                dish.c.name.label("dish_name"),
                t.c.ingredient_id,
                ingredient.c.name.label("ingredient_name"),
                t.c.quantity,
                t.c.unit,
                dish.c.created_on.label("used_on"),
                sa_total_count(t.c.id),
            )
            .select_from(
                t.join(dish, t.c.dish_id == dish.c.id)
                .join(
                    ingredient_in_inventory,
                    t.c.ingredient_id == ingredient_in_inventory.c.id,
                )
                .join(
                    ingredient,
                    ingredient.c.id == ingredient_in_inventory.c.ingredient_id,
                )
            )
            .where(t.c.dish_id == dish_id)
            .order_by(t.c.id)
            .offset(params.offset)
            .limit(params.limit)
        )

        if params.ingredient_name:
            stmt = stmt.where(ingredient.c.name == params.ingredient_name)
        if params.ingredient_name__contains:
            stmt = stmt.where(
                ingredient.c.name.contains(params.ingredient_name__contains)
            )

        res = await transaction.execute(stmt)
        results = [dict(r) for r in res.mappings()]
        page = paginator.get(results, request_url, params.offset, params.limit)
        return cls.model_validate(
            {
                "total_count": page.total_count,
                "next_url": page.next_url,
                "results": results,
            }
        )
