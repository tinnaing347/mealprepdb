from typing import Dict, Optional, List
from ..base import (
    IngredientTypeEnum,
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
from .. import paginator


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

    @classmethod
    async def detail(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
    ) -> "IngredientResource":
        t = transaction.get_table("ingredient")
        stmt = (
            sa.select(t.c.id, t.c.name, t.c.type)
            .order_by(t.c.id)
            .where(t.c.id == obj_id)
        )

        res = await transaction.execute(stmt)
        result = res.one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found.")

        return cls.model_validate(result)


class IngredientListView(ListViewModel[IngredientResource]):
    results: List[IngredientResource]

    @classmethod
    async def get(
        cls,
        transaction: dal.TransactionManager,
        request_url: str,
        params: IngredientQueryParams,
    ) -> "IngredientListView":
        t = transaction.get_table("ingredient")
        stmt = (
            sa.select(
                t.c.id,
                t.c.name,
                t.c.type,
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
        if params.type:
            stmt = stmt.where(t.c.type == params.type)

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
