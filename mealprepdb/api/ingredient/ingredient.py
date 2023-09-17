from typing import Dict, Optional, Any, List
import dataclasses
from ..base import (
    IngredientTypeEnum,
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


class IngredientQueryParams(BaseListViewQueryParamsModel):
    def __init__(
        self,
        name__contains: str = Query(None),
        name: str = Query(None),
        type: IngredientTypeEnum = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.name__contains = name__contains
        self.name = name
        self.offset = offset
        self.limit = limit
        self.type = type


@dataclasses.dataclass
class IngredientData:
    id: int = 0
    name: str = ""
    type: IngredientTypeEnum = IngredientTypeEnum._default


@dataclasses.dataclass
class IngredientListViewEntity(IngredientData, Paginateable):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: IngredientQueryParams
    ) -> sa.Select[Any]:
        t = transaction.get_table("ingredient")
        stmt = (
            sa.select(
                t.c.id,
                t.c.name,
                t.c.type,
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
        if where.type:
            stmt = stmt.where(t.c.type == where.type)

        return stmt


@dataclasses.dataclass
class IngredientDetailViewEntity(IngredientData, dbentity.Queryable[ObjectIdFromUrl]):
    @classmethod
    def query_stmt(
        cls, transaction: dal.TransactionManager, where: ObjectIdFromUrl
    ) -> sa.Select[Any]:
        t = transaction.get_table("ingredient")
        stmt = (
            sa.select(t.c.id, t.c.name, t.c.type)
            .order_by(t.c.id)
            .where(t.c.id == where.obj_id)
        )
        return stmt


class IngredientListQ(query.ListQ[IngredientListViewEntity, IngredientQueryParams]):
    __db_obj__ = IngredientListViewEntity


class IngredientDetailQ(query.DetailQ[IngredientDetailViewEntity, ObjectIdFromUrl]):
    __db_obj__ = IngredientDetailViewEntity


class IngredientResource(ParentResourceModel):
    id: int
    name: str
    type: Optional[IngredientTypeEnum] = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for("ingredient_detail_view", id=self.id)
            }
        return None


class IngredientListView(ListViewModel[IngredientResource]):
    results: List[IngredientResource]
