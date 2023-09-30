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


class MealIngredientQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        ingredient_name: str = Query(None),
        ingredient_name__contains: str = Query(None),
        consumed_on: datetime.date = Query(None),
        consumed_on__le: datetime.date = Query(None),
        consumed_on__ge: datetime.date = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.ingredient_name = ingredient_name
        self.ingredient_name__contains = ingredient_name__contains
        self.consumed_on = consumed_on
        self.consumed_on__ge = consumed_on__ge
        self.consumed_on__le = consumed_on__le
        self.offset = offset
        self.limit = limit


@dataclasses.dataclass
class MealIngredientData:
    id: int = 0
    meal_type: str = ""
    meal_id: int = 0
    ingredient_name: str = ""
    ingredient_id: int = 0
    quantity: float = 0.0
    unit: str = ""
    consumed_on: datetime.date = datetime.date(1970, 1, 1)


@dataclasses.dataclass
class PrivateMealIngredientQueryParams:
    params: MealIngredientQueryParams
    ingredient_id: int = 0


# this can become a cte; then filter on meal_id or ingredient
@dataclasses.dataclass
class MealIngredientListViewEntity(MealIngredientData, Paginateable):
    @classmethod
    def query_stmt(
        cls,
        transaction: dal.TransactionManager,
        where: PrivateMealIngredientQueryParams,
    ) -> sa.Select[Any]:
        meal = transaction.get_table("meal")
        ingredient = transaction.get_table("ingredient")
        ingredient_in_inventory = transaction.get_table("ingredient_in_inventory")
        t = transaction.get_table("meal_ingredient")

        stmt = (
            sa.select(
                t.c.id,
                meal.c.type.label("meal_type"),
                t.c.meal_id,
                ingredient.c.name.label("ingredient_name"),
                t.c.ingredient_id,
                t.c.quantity,
                t.c.unit,
                meal.c.consumed_on,
                sa_total_count(t.c.id),
            )
            .select_from(
                t.join(
                    ingredient_in_inventory,
                    t.c.ingredient_id == ingredient_in_inventory.c.id,
                )
                .join(ingredient, t.c.ingredient_id == ingredient.c.id)
                .join(meal, t.c.meal_id == meal.c.id)
            )
            .order_by(t.c.id)
            .offset(where.params.offset)
            .limit(where.params.limit)
        )

        if where.ingredient_id:
            stmt = stmt.where(t.c.ingredient_id == where.ingredient_id)

        if where.params.ingredient_name:
            stmt = stmt.where(ingredient.c.name == where.params.ingredient_name)
        if where.params.ingredient_name__contains:
            stmt = stmt.where(
                ingredient.c.name.contains(where.params.ingredient_name__contains)
            )
        if where.params.consumed_on:
            stmt = stmt.where(meal.c.consumed_on == where.params.consumed_on)
        if where.params.consumed_on__le:
            stmt = stmt.where(meal.c.consumed_on <= where.params.consumed_on__le)
        if where.params.consumed_on__ge:
            stmt = stmt.where(meal.c.consumed_on >= where.params.consumed_on__ge)

        return stmt


@dataclasses.dataclass
class MealIngredientDetailViewEntity(
    MealIngredientData, dbentity.Queryable[ObjectIdFromUrl]
):
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


class MealIngredientListQ(
    query.ListQ[MealIngredientListViewEntity, PrivateMealIngredientQueryParams]
):
    __db_obj__ = MealIngredientListViewEntity


class MealIngredientDetailQ(
    query.DetailQ[MealIngredientDetailViewEntity, ObjectIdFromUrl]
):
    __db_obj__ = MealIngredientDetailViewEntity


class MealIngredientResource(ParentResourceModel):
    id: int
    meal_type: str
    meal_id: int
    ingredient_name: str
    ingredient_id: int
    quantity: float
    unit: str
    consumed_on: datetime.date

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "ingredient": self._fastapi.url_path_for(
                    "ingredient_detail_view", id=self.ingredient_id
                ),
                "meal": self._fastapi.url_path_for("meal_detail_view", id=self.meal_id),
            }
        return None


class MealIngredientListView(ListViewModel[MealIngredientResource]):
    results: List[MealIngredientResource]
