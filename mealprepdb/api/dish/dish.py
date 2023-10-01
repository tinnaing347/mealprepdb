from typing import Dict, Optional, Any, List
from ..base import (
    BaseListViewQueryParamsModel,
    ListViewModel,
    ResourceUri,
    ParentResourceModel,
)
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query, HTTPException
import pydantic
import datetime
from .. import paginator


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

    @classmethod
    async def detail(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
    ) -> "DishResource":
        t = transaction.get_table("dish")
        stmt = (
            sa.select(t.c.id, t.c.name, t.c.parent_dish_id, t.c.created_on)
            .order_by(t.c.id)
            .where(t.c.id == obj_id)
        )
        res = await transaction.execute(stmt)
        result = res.one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found.")

        return cls.model_validate(result)


class DishListView(ListViewModel[DishResource]):
    results: List[DishResource]

    @classmethod
    async def get(
        cls,
        transaction: dal.TransactionManager,
        request_url: str,
        params: DishQueryParams,
    ) -> "DishListView":
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
            .offset(params.offset)
            .limit(params.limit)
        )

        if params.name:
            stmt = stmt.where(t.c.name == params.name)
        if params.name__contains:
            stmt = stmt.where(t.c.name.contains(params.name__contains))
        if params.created_on:
            stmt = stmt.where(t.c.created_on == params.created_on)
        if params.created_on__le:
            stmt = stmt.where(t.c.created_on <= params.created_on__le)
        if params.created_on__ge:
            stmt = stmt.where(t.c.created_on >= params.created_on__ge)

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
