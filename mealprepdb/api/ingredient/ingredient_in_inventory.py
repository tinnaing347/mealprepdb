from typing import Dict, Optional, Any, List
import dataclasses
from .. import base
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query, HTTPException
import pydantic
import datetime
from .. import paginator


class IngredientInInventoryQueryParams(base.BaseListViewQueryParamsModel):
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
class IngredientInInventoryListViewEntity(IngredientInInventoryData, base.Paginateable):
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


class IngredientInInventoryBaseForm(base.BaseFormModel):
    name: str | None = ""
    ingredient_id: int | None = None
    from_where: str | None = ""
    brand: str | None = ""
    quantity: int | None = None
    unit: str | None = ""
    purchased_on: datetime.date | None = None
    finished_on: datetime.date | None = None


class IngredientInInventoryCreateForm(IngredientInInventoryBaseForm):
    ingredient_id: int


class IngredientInInventoryUpdateForm(IngredientInInventoryBaseForm):
    ...


class IngredientInInventoryResource(base.ParentResourceModel):
    id: int
    name: str
    ingredient_id: int
    from_where: str | None = ""
    brand: str | None = ""
    quantity: Optional[float] = None
    unit: str | None = ""
    purchased_on: datetime.date | None = None
    finished_on: datetime.date | None = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, base.ResourceUri]]:
        if self._fastapi:
            return {
                "self": self._fastapi.url_path_for(
                    "ingredient_in_inventory_detail_view", id=self.id
                ),
                "ingredient": self._fastapi.url_path_for(
                    "ingredient_detail_view", id=self.ingredient_id
                ),
                "ingredient_meal": self._fastapi.url_path_for(
                    "ingredient_meal_list_view", id=self.id
                ),
            }
        return None

    @classmethod
    async def detail(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
    ) -> "IngredientInInventoryResource":
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
            .where(t.c.id == obj_id)
            .order_by(ing.c.name, t.c.purchased_on)
        )

        res = await transaction.execute(stmt)
        result = res.one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Not Found.")

        return cls.model_validate(result)

    @classmethod
    async def create(
        cls, transaction: dal.TransactionManager, form: IngredientInInventoryCreateForm
    ) -> "IngredientInInventoryResource":
        result = await base.create(
            transaction,
            tablename="ingredient_in_inventory",
            form_data=form.model_dump(),
        )
        return cls.model_validate(result)

    @classmethod
    async def update(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
        form: IngredientInInventoryUpdateForm,
    ) -> "IngredientInInventoryResource":
        result = await base.update(
            transaction,
            tablename="ingredient_in_inventory",
            obj_id=obj_id,
            form_data=form.model_dump(exclude_unset=True),
        )
        return cls.model_validate(result)


class IngredientInInventoryListView(base.ListViewModel[IngredientInInventoryResource]):
    results: List[IngredientInInventoryResource]

    @classmethod
    async def get(
        cls,
        transaction: dal.TransactionManager,
        request_url: str,
        params: IngredientInInventoryQueryParams,
    ) -> "IngredientInInventoryListView":
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
            .offset(params.offset)
            .limit(params.limit)
        )

        if params.name:
            stmt = stmt.where(ing.c.name == params.name)
        if params.name__contains:
            stmt = stmt.where(ing.c.name.contains(params.name__contains))
        if params.from_where:
            stmt = stmt.where(t.c.from_where == params.from_where)
        if params.from_where__contains:
            stmt = stmt.where(t.c.from_where.contains(params.from_where__contains))

        if params.purchased_on:
            stmt = stmt.where(t.c.purchased_on == params.purchased_on)
        if params.purchased_on__le:
            stmt = stmt.where(t.c.purchased_on <= params.purchased_on__le)
        if params.purchased_on__ge:
            stmt = stmt.where(t.c.purchased_on >= params.purchased_on__ge)

        if params.finished_on:
            stmt = stmt.where(t.c.finished_on == params.finished_on)
        if params.finished_on__le:
            stmt = stmt.where(t.c.finished_on <= params.finished_on__le)
        if params.finished_on__ge:
            stmt = stmt.where(t.c.finished_on >= params.finished_on__ge)

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
