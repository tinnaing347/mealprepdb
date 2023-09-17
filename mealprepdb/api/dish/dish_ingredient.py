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


@dataclasses.dataclass
class DishIngredientData:
    id: int = 0
    dish_id: int = 0
    dish_name: str = ""
    ingredient_id: int = 0
    ingredient_name: str = ""
    quantity: Optional[float] = None
    unit: Optional[str] = None
    used_on: Optional[datetime.date] = None


@dataclasses.dataclass
class PrivateDishIngredientQueryParams:
    dish_id: int
    params: DishIngredientQueryParams


@dataclasses.dataclass
class DishIngredientListViewEntity(DishIngredientData, Paginateable):
    @classmethod
    def query_stmt(
        cls,
        transaction: dal.TransactionManager,
        where: PrivateDishIngredientQueryParams,
    ) -> sa.Select[Any]:
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
            .where(t.c.dish_id == where.dish_id)
            .order_by(t.c.id)
            .offset(where.params.offset)
            .limit(where.params.limit)
        )

        if where.params.ingredient_name:
            stmt = stmt.where(ingredient.c.name == where.params.ingredient_name)
        if where.params.ingredient_name__contains:
            stmt = stmt.where(
                ingredient.c.name.contains(where.params.ingredient_name__contains)
            )

        return stmt


# @dataclasses.dataclass
# class DishIngredientDetailViewEntity(
#     DishIngredientData, dbentity.Queryable[ObjectIdFromUrl]
# ):
#     @classmethod
#     def query_stmt(
#         cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
#     ) -> sa.Select[Any]:
#         pass


class DishIngredientListQ(
    query.ListQ[DishIngredientListViewEntity, PrivateDishIngredientQueryParams]
):
    __db_obj__ = DishIngredientListViewEntity


# XXX may not be useful
# class DishIngredientDetailQ(
#     query.DetailQ[DishIngredientDetailViewEntity, ObjectIdFromUrl]
# ):
#     __db_obj__ = DishIngredientDetailViewEntity


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
