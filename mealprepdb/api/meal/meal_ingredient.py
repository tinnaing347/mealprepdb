from typing import Dict, Optional, List
from .. import base
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query
import pydantic
import datetime
from .. import paginator


class MealIngredientQueryParams(base.BaseListViewQueryParamsModel):
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


class MealIngredientBaseForm(base.BaseFormModel):
    meal_id: int | None = None
    ingredient_id: int | None = None
    quantity: float | None = None
    unit: str | None = None


class MealIngredientCreateForm(MealIngredientBaseForm):
    meal_id: int
    ingredient_id: int
    quantity: float
    unit: str


class MealIngredientUpdateForm(MealIngredientBaseForm):
    ...


class MealIngredientResource(base.ParentResourceModel):
    id: int
    meal_id: int
    ingredient_id: int
    quantity: float
    unit: str

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, base.ResourceUri]]:
        if self._fastapi:
            return {
                "ingredient": self._fastapi.url_path_for(
                    "ingredient_detail_view", id=self.ingredient_id
                ),
                "meal": self._fastapi.url_path_for("meal_detail_view", id=self.meal_id),
            }
        return None

    @classmethod
    async def create(
        cls, transaction: dal.TransactionManager, form: MealIngredientCreateForm
    ) -> "MealIngredientResource":
        result = await base.create(
            transaction, tablename="meal_ingredient", form_data=form.model_dump()
        )
        return cls.model_validate(result)

    @classmethod
    async def update(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
        form: MealIngredientUpdateForm,
    ) -> "MealIngredientResource":
        result = await base.update(
            transaction,
            tablename="meal_ingredient",
            obj_id=obj_id,
            form_data=form.model_dump(exclude_unset=True),
        )
        return cls.model_validate(result)


class MealIngredientDetailResource(MealIngredientResource):
    meal_type: str
    ingredient_name: str
    consumed_on: datetime.date


class MealIngredientListView(base.ListViewModel[MealIngredientDetailResource]):
    results: List[MealIngredientDetailResource]

    @classmethod
    async def from_ingredient(
        cls,
        transaction: dal.TransactionManager,
        ingredient_id: int,
        request_url: str,
        params: MealIngredientQueryParams,
    ) -> "MealIngredientListView":
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
            .where(t.c.ingredient_id == ingredient_id)
            .order_by(t.c.id)
            .offset(params.offset)
            .limit(params.limit)
        )

        if params.ingredient_name:
            stmt = stmt.where(ingredient.c.name == params.ingredient_name)
        if params.ingredient_name__contains:
            stmt = stmt.where(
                ingredient.c.name.contains(params.ingredient_name__contains)
            )
        if params.consumed_on:
            stmt = stmt.where(meal.c.consumed_on == params.consumed_on)
        if params.consumed_on__le:
            stmt = stmt.where(meal.c.consumed_on <= params.consumed_on__le)
        if params.consumed_on__ge:
            stmt = stmt.where(meal.c.consumed_on >= params.consumed_on__ge)

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
