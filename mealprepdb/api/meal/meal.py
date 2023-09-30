from typing import Dict, Optional, Any, List
import dataclasses
from ..base import (
    Paginateable,
    BaseListViewQueryParamsModel,
    ListViewModel,
    ObjectIdFromUrl,
    ResourceUri,
    ParentResourceModel,
    MealTypeEnum,
)
from aiodal import dal
from aiodal.oqm import dbentity, query
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query
import pydantic
import datetime


class MealQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        type: MealTypeEnum = Query(None),
        consumed_on: datetime.date = Query(None),
        consumed_on__le: datetime.date = Query(None),
        consumed_on__ge: datetime.date = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.type = type
        self.consumed_on = consumed_on
        self.consumed_on__ge = consumed_on__ge
        self.consumed_on__le = consumed_on__le
        self.offset = offset
        self.limit = limit


@dataclasses.dataclass
class MealData:
    id: int = 0
    type: MealTypeEnum = MealTypeEnum._default
    description: str = ""
    consumed_on: datetime.date = datetime.date(1970, 1, 1)


@dataclasses.dataclass
class MealListViewEntity(MealData, Paginateable):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: MealQueryParams
    ) -> sa.Select[Any]:
        t = transaction.get_table("meal")
        stmt = (
            sa.select(
                t.c.id,
                t.c.type,
                t.c.description,
                t.c.consumed_on,
                sa_total_count(t.c.id),
            )
            .order_by(t.c.id)
            .offset(where.offset)
            .limit(where.limit)
        )

        if where.type:
            stmt = stmt.where(t.c.type == where.type)
        if where.consumed_on:
            stmt = stmt.where(t.c.consumed_on == where.consumed_on)
        if where.consumed_on__le:
            stmt = stmt.where(t.c.consumed_on <= where.consumed_on__le)
        if where.consumed_on__ge:
            stmt = stmt.where(t.c.consumed_on >= where.consumed_on__ge)

        return stmt


@dataclasses.dataclass
class MealDetailViewEntity(MealData, dbentity.Queryable[ObjectIdFromUrl]):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
    ) -> sa.Select[Any]:
        t = transaction.get_table("meal")
        stmt = (
            sa.select(t.c.id, t.c.type, t.c.description, t.c.consumed_on)
            .order_by(t.c.id)
            .where(t.c.id == where.obj_id)
        )
        return stmt


class MealListQ(query.ListQ[MealListViewEntity, MealQueryParams]):
    __db_obj__ = MealListViewEntity


class MealDetailQ(query.DetailQ[MealDetailViewEntity, ObjectIdFromUrl]):
    __db_obj__ = MealDetailViewEntity


class MealResource(ParentResourceModel):
    id: int
    type: Optional[MealTypeEnum] = None
    description: str = ""
    consumed_on: datetime.date

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for("meal_detail_view", id=self.id),
            }
        return None


class MealListView(ListViewModel[MealResource]):
    results: List[MealResource]
