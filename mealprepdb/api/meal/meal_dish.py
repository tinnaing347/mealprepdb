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


class MealDishQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        dish_name: str = Query(None),
        dish_name__contains: str = Query(None),
        consumed_on: datetime.date = Query(None),
        consumed_on__le: datetime.date = Query(None),
        consumed_on__ge: datetime.date = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.dish_name = dish_name
        self.dish_name__contains = dish_name__contains
        self.consumed_on = consumed_on
        self.consumed_on__ge = consumed_on__ge
        self.consumed_on__le = consumed_on__le
        self.offset = offset
        self.limit = limit


@dataclasses.dataclass
class MealDishData:
    id: int = 0
    meal_type: str = ""
    meal_id: int = 0
    dish_name: str = ""
    dish_id: int = 0
    quantity: float = 0.0
    unit: str = ""
    consumed_on: datetime.date = datetime.date(1970, 1, 1)
    dish_created_on: datetime.date = datetime.date(1970, 1, 1)


@dataclasses.dataclass
class PrivateMealDishQueryParams:
    params: MealDishQueryParams
    dish_id: int = 0


# this can become a cte; then filter on meal_id or dish
@dataclasses.dataclass
class MealDishListViewEntity(MealDishData, Paginateable):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: PrivateMealDishQueryParams
    ) -> sa.Select[Any]:
        meal = transaction.get_table("meal")
        dish = transaction.get_table("dish")
        t = transaction.get_table("meal_dish")
        stmt = (
            sa.select(
                t.c.id,
                meal.c.type.label("meal_type"),
                t.c.meal_id,
                dish.c.name.label("dish_name"),
                t.c.dish_id,
                t.c.quantity,
                t.c.unit,
                meal.c.consumed_on,
                dish.c.created_on.label("dish_created_on"),
                sa_total_count(t.c.id),
            )
            .select_from(
                t.join(dish, t.c.dish_id == dish.c.id).join(
                    meal, t.c.meal_id == meal.c.id
                )
            )
            .order_by(t.c.id)
            .offset(where.params.offset)
            .limit(where.params.limit)
        )
        if where.dish_id:
            stmt = stmt.where(t.c.dish_id == where.dish_id)

        if where.params.dish_name:
            stmt = stmt.where(dish.c.name == where.params.dish_name)
        if where.params.dish_name__contains:
            stmt = stmt.where(dish.c.name.contains(where.params.dish_name__contains))
        if where.params.consumed_on:
            stmt = stmt.where(t.c.consumed_on == where.params.consumed_on)
        if where.params.consumed_on__le:
            stmt = stmt.where(t.c.consumed_on <= where.params.consumed_on__le)
        if where.params.consumed_on__ge:
            stmt = stmt.where(t.c.consumed_on >= where.params.consumed_on__ge)

        return stmt


@dataclasses.dataclass
class MealDishDetailViewEntity(MealDishData, dbentity.Queryable[ObjectIdFromUrl]):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
    ) -> sa.Select[Any]:
        t = transaction.get_table("meal")
        stmt = (
            sa.select(t.c.id, t.c.type, t.c.consumed_on)
            .order_by(t.c.id)
            .where(t.c.id == where.obj_id)
        )
        return stmt


class MealDishListQ(query.ListQ[MealDishListViewEntity, PrivateMealDishQueryParams]):
    __db_obj__ = MealDishListViewEntity


class MealDishDetailQ(query.DetailQ[MealDishDetailViewEntity, ObjectIdFromUrl]):
    __db_obj__ = MealDishDetailViewEntity


class MealDishResource(ParentResourceModel):
    id: int
    meal_type: str
    meal_id: int
    dish_name: str
    dish_id: int
    quantity: float
    unit: str
    consumed_on: Optional[datetime.date] = None
    dish_created_on: Optional[datetime.date] = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for("meal_detail_view", id=self.id),
                "dish": self._fastapi.url_path_for("dish_detail_view", id=self.dish_id),
                "meal": self._fastapi.url_path_for("meal_detail_view", id=self.meal_id),
            }
        return None


class MealDishListView(ListViewModel[MealDishResource]):
    results: List[MealDishResource]
