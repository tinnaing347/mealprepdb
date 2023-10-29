from typing import Dict, Optional, List
from .. import base
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query
import pydantic
import datetime
from .. import paginator


class MealDishQueryParams(base.BaseListViewQueryParamsModel):
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


class MealDishBaseForm(base.BaseFormModel):
    meal_id: int | None = None
    dish_id: int | None = None
    quantity: float | None = None
    unit: str | None = None


class MealDishCreateForm(MealDishBaseForm):
    meal_id: int
    dish_id: int
    quantity: float
    unit: str


class MealDishUpdateForm(MealDishBaseForm):
    ...


class MealDishResource(base.ParentResourceModel):
    id: int
    meal_id: int
    dish_id: int

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, base.ResourceUri]]:
        if self._fastapi:
            return {
                "dish": self._fastapi.url_path_for("dish_detail_view", id=self.dish_id),
                "meal": self._fastapi.url_path_for("meal_detail_view", id=self.meal_id),
            }
        return None

    @classmethod
    async def create(
        cls, transaction: dal.TransactionManager, form: MealDishCreateForm
    ) -> "MealDishResource":
        result = await base.create(
            transaction, tablename="meal_dish", form_data=form.model_dump()
        )
        return cls.model_validate(result)

    @classmethod
    async def update(
        cls, transaction: dal.TransactionManager, obj_id: int, form: MealDishUpdateForm
    ) -> "MealDishResource":
        result = await base.update(
            transaction,
            tablename="meal_dish",
            obj_id=obj_id,
            form_data=form.model_dump(exclude_unset=True),
        )
        return cls.model_validate(result)


class MealDishDetailResource(MealDishResource):
    meal_type: str
    dish_name: str
    quantity: float
    unit: str
    consumed_on: Optional[datetime.date] = None
    dish_created_on: Optional[datetime.date] = None


class MealDishListView(base.ListViewModel[MealDishDetailResource]):
    results: List[MealDishDetailResource]

    @classmethod
    async def from_dish(
        cls,
        transaction: dal.TransactionManager,
        dish_id: int,
        request_url: str,
        params: MealDishQueryParams,
    ) -> "MealDishListView":
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
            .where(t.c.dish_id == dish_id)
            .order_by(t.c.id)
            .offset(params.offset)
            .limit(params.limit)
        )
        if params.dish_name:
            stmt = stmt.where(dish.c.name == params.dish_name)
        if params.dish_name__contains:
            stmt = stmt.where(dish.c.name.contains(params.dish_name__contains))
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
