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


class IngredientInInventoryQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        name: str = Query(None),
        name__contains: str = Query(None),
        from_where: str = Query(None),
        from_where__contains: str = Query(None),
        purchased_on: datetime.date = Query(None),
        purchased_on__le: datetime.date = Query(None),
        purchased_on__ge: datetime.date = Query(None),
        finished_on: datetime.date = Query(None),
        finished_on__le: datetime.date = Query(None),
        finished_on__ge: datetime.date = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.name__contains = name__contains
        self.name = name
        self.from_where = from_where
        self.from_where__contains = from_where__contains

        self.purchased_on = purchased_on
        self.purchased_on__ge = purchased_on__ge
        self.purchased_on__le = purchased_on__le

        self.finished_on = finished_on
        self.finished_on__ge = finished_on__ge
        self.finished_on__le = finished_on__le

        self.offset = offset
        self.limit = limit


@dataclasses.dataclass
class IngredientInInventoryData:
    id: int = 0
    name: str = ""
    ingredient_id: int = 0
    from_where: str = ""
    brand: str = ""
    quantity: Optional[float] = None
    unit: Optional[str] = None
    purchased_on: Optional[datetime.date] = None
    finished_on: Optional[datetime.date] = None


@dataclasses.dataclass
class IngredientInInventoryListViewEntity(IngredientInInventoryData, Paginateable):
    @classmethod
    def query_stmt(
        cls,
        transaction: dal.TransactionManager,
        where: IngredientInInventoryQueryParams,
    ) -> sa.Select[Any]:
        ing = transaction.get_table("ingredient")
        t = transaction.get_table("ingredient_in_inventory")
        stmt = (
            sa.select(
                t.c.id,
                ing.c.name,
                t.c.ingredient_id,
                t.c.from_where,
                t.c.brand,
                t.c.quantity,
                t.c.unit,
                t.c.purchased_on,
                t.c.finished_on,
                sa_total_count(t.c.id),
            )
            .select_from(t.join(ing, t.c.ingredient_id == ing.c.id))
            .order_by(ing.c.name, t.c.purchased_on)
            .offset(where.offset)
            .limit(where.limit)
        )

        if where.name:
            stmt = stmt.where(ing.c.name == where.name)
        if where.name__contains:
            stmt = stmt.where(ing.c.name.contains(where.name__contains))
        if where.from_where:
            stmt = stmt.where(t.c.from_where == where.from_where)
        if where.from_where__contains:
            stmt = stmt.where(t.c.from_where.contains(where.from_where__contains))

        if where.purchased_on:
            stmt = stmt.where(t.c.purchased_on == where.purchased_on)
        if where.purchased_on__le:
            stmt = stmt.where(t.c.purchased_on <= where.purchased_on__le)
        if where.purchased_on__ge:
            stmt = stmt.where(t.c.purchased_on >= where.purchased_on__ge)

        if where.finished_on:
            stmt = stmt.where(t.c.finished_on == where.finished_on)
        if where.finished_on__le:
            stmt = stmt.where(t.c.finished_on <= where.finished_on__le)
        if where.finished_on__ge:
            stmt = stmt.where(t.c.finished_on >= where.finished_on__ge)

        return stmt


@dataclasses.dataclass
class IngredientInInventoryDetailViewEntity(
    IngredientInInventoryData, dbentity.Queryable[ObjectIdFromUrl]
):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
    ) -> sa.Select[Any]:
        ing = transaction.get_table("ingredient")
        t = transaction.get_table("ingredient_in_inventory")
        stmt = (
            sa.select(
                t.c.id,
                ing.c.name,
                t.c.ingredient_id,
                t.c.from_where,
                t.c.brand,
                t.c.quantity,
                t.c.unit,
                t.c.purchased_on,
                t.c.finished_on,
            )
            .select_from(t.join(ing, t.c.ingredient_id == ing.c.id))
            .where(t.c.id == where.obj_id)
            .order_by(ing.c.name, t.c.purchased_on)
        )

        return stmt


class IngredientInInventoryListQ(
    query.ListQ[IngredientInInventoryListViewEntity, IngredientInInventoryQueryParams]
):
    __db_obj__ = IngredientInInventoryListViewEntity


class IngredientInInventoryDetailQ(
    query.DetailQ[IngredientInInventoryDetailViewEntity, ObjectIdFromUrl]
):
    __db_obj__ = IngredientInInventoryDetailViewEntity


class IngredientInInventoryResource(ParentResourceModel):
    id: int
    name: str
    ingredient_id: int
    from_where: Optional[str] = ""
    brand: Optional[str] = ""
    quantity: Optional[float] = None
    unit: Optional[str] = ""
    purchased_on: Optional[datetime.date] = None
    finished_on: Optional[datetime.date] = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for(
                    "ingredient_in_inventory_detail_view", id=self.id
                )
            }
        return None


class IngredientInInventoryListView(ListViewModel[IngredientInInventoryResource]):
    results: List[IngredientInInventoryResource]
