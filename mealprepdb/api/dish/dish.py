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


class DishQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        name__contains: str = Query(None),
        name: str = Query(None),
        created_on: datetime.date = Query(None),
        created_on__le: datetime.date = Query(None),
        created_on__ge: datetime.date = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.name__contains = name__contains
        self.name = name
        self.created_on = created_on
        self.created_on__ge = created_on__ge
        self.created_on__le = created_on__le
        self.offset = offset
        self.limit = limit


@dataclasses.dataclass
class DishData:
    id: int = 0
    name: str = ""
    parent_dish_id: Optional[int] = None
    created_on: Optional[datetime.date] = None


@dataclasses.dataclass
class DishListViewEntity(DishData, Paginateable):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: DishQueryParams
    ) -> sa.Select[Any]:
        t = transaction.get_table("dish")
        stmt = (
            sa.select(
                t.c.id,
                t.c.name,
                t.c.parent_dish_id,
                t.c.created_on,
                sa_total_count(t.c.id),
            )
            .order_by(t.c.id)
            .offset(where.offset)
            .limit(where.limit)
        )

        if where.name:
            stmt = stmt.where(t.c.name == where.name)
        if where.name__contains:
            stmt = stmt.where(t.c.name.contains(where.name__contains))
        if where.created_on:
            stmt = stmt.where(t.c.created_on == where.created_on)
        if where.created_on__le:
            stmt = stmt.where(t.c.created_on <= where.created_on__le)
        if where.created_on__ge:
            stmt = stmt.where(t.c.created_on >= where.created_on__ge)

        return stmt


@dataclasses.dataclass
class DishDetailViewEntity(DishData, dbentity.Queryable[ObjectIdFromUrl]):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
    ) -> sa.Select[Any]:
        t = transaction.get_table("dish")
        stmt = (
            sa.select(t.c.id, t.c.name, t.c.parent_dish_id, t.c.created_on)
            .order_by(t.c.id)
            .where(t.c.id == where.obj_id)
        )
        return stmt


class DishListQ(query.ListQ[DishListViewEntity, DishQueryParams]):
    __db_obj__ = DishListViewEntity


class DishDetailQ(query.DetailQ[DishDetailViewEntity, ObjectIdFromUrl]):
    __db_obj__ = DishDetailViewEntity


class DishResource(ParentResourceModel):
    id: int
    name: str
    parent_dish_id: Optional[int] = None
    created_on: Optional[datetime.date] = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for("dish_detail_view", id=self.id),
                "dish_ingredient": self._fastapi.url_path_for(
                    "dish_ingredient_list_view", id=self.id
                ),
                "dish_meal": self._fastapi.url_path_for(
                    "dish_meal_list_view", id=self.id
                ),
            }
        return None


class DishListView(ListViewModel[DishResource]):
    results: List[DishResource]
