from typing import Dict, Optional, Any, List
from .. import base
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query, HTTPException
import pydantic
import datetime
from .. import paginator


class MealQueryParams(base.BaseListViewQueryParamsModel):
    def __init__(
        self,
        type: base.MealTypeEnum = Query(None),
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


class MealBaseForm(base.BaseFormModel):
    type: base.MealTypeEnum | None = None
    description: str | None = None
    consumed_on: datetime.date | None = None


class MealCreateForm(MealBaseForm):
    description: str
    consumed_on: datetime.date


class MealUpdateForm(MealBaseForm):
    ...


class MealResource(base.ParentResourceModel):
    id: int
    type: base.MealTypeEnum | None = None
    description: str = ""
    consumed_on: datetime.date

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, base.ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for("meal_detail_view", id=self.id),
            }
        return None

    @classmethod
    async def detail(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
    ) -> "MealResource":
        t = transaction.get_table("meal")
        stmt = (
            sa.select(t.c.id, t.c.type, t.c.description, t.c.consumed_on)
            .order_by(t.c.id)
            .where(t.c.id == obj_id)
        )
        res = await transaction.execute(stmt)
        result = res.one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found.")

        return cls.model_validate(result)

    @classmethod
    async def create(
        cls, transaction: dal.TransactionManager, form: MealCreateForm
    ) -> "MealResource":
        result = await base.create(
            transaction, tablename="meal", form_data=form.model_dump()
        )
        return cls.model_validate(result)

    @classmethod
    async def update(
        cls, transaction: dal.TransactionManager, obj_id: int, form: MealUpdateForm
    ) -> "MealResource":
        result = await base.update(
            transaction,
            tablename="meal",
            obj_id=obj_id,
            form_data=form.model_dump(exclude_unset=True),
        )
        return cls.model_validate(result)


class MealListView(base.ListViewModel[MealResource]):
    results: List[MealResource]

    @classmethod
    async def get(
        cls,
        transaction: dal.TransactionManager,
        request_url: str,
        params: MealQueryParams,
    ) -> "MealListView":
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
            .offset(params.offset)
            .limit(params.limit)
        )

        if params.type:
            stmt = stmt.where(t.c.type == params.type)
        if params.consumed_on:
            stmt = stmt.where(t.c.consumed_on == params.consumed_on)
        if params.consumed_on__le:
            stmt = stmt.where(t.c.consumed_on <= params.consumed_on__le)
        if params.consumed_on__ge:
            stmt = stmt.where(t.c.consumed_on >= params.consumed_on__ge)

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
