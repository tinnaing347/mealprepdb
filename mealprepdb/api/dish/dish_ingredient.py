from typing import Dict, Optional, List
from .. import base
from aiodal import dal
from aiodal.helpers import sa_total_count
import sqlalchemy as sa
from fastapi import Query
import pydantic
import datetime
from .. import paginator


class DishIngredientQueryParams(base.BaseListViewQueryParamsModel):
    def __init__(
        self,
        ingredient_name__contains: str = Query(None),
        ingredient_name: str = Query(None),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=0, le=2000),
    ):
        self.ingredient_name__contains = ingredient_name__contains
        self.ingredient_name = ingredient_name
        self.offset = offset
        self.limit = limit


class DishIngredientBaseForm(base.BaseFormModel):
    dish_id: int | None = None
    ingredient_id: int | None = None
    quantity: float | None = None
    unit: str | None = None


class DishIngredientCreateForm(DishIngredientBaseForm):
    dish_id: int
    ingredient_id: int


class DishIngredientUpdateForm(DishIngredientBaseForm):
    ...


class DishIngredientResource(base.ParentResourceModel):
    id: int
    dish_id: int
    ingredient_id: int
    quantity: float | None = None
    unit: str | None = None

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, base.ResourceUri]]:
        if self._fastapi:
            return {
                "dish": self._fastapi.url_path_for("dish_detail_view", id=self.dish_id),
                "ingredient_in_inventory": self._fastapi.url_path_for(
                    "ingredient_in_inventory_detail_view", id=self.ingredient_id
                ),
            }
        return None

    @classmethod
    async def create(
        cls, transaction: dal.TransactionManager, form: DishIngredientCreateForm
    ) -> "DishIngredientResource":
        result = await base.create(
            transaction, tablename="dish_ingredient", form_data=form.model_dump()
        )
        return cls.model_validate(result)

    @classmethod
    async def update(
        cls,
        transaction: dal.TransactionManager,
        obj_id: int,
        form: DishIngredientUpdateForm,
    ) -> "DishIngredientResource":
        result = await base.update(
            transaction,
            tablename="dish_ingredient",
            obj_id=obj_id,
            form_data=form.model_dump(exclude_unset=True),
        )
        return cls.model_validate(result)


class DishIngredientDetailResource(DishIngredientResource):
    dish_name: str
    ingredient_name: str
    used_on: datetime.date | None = None


class DishIngredientListView(base.ListViewModel[DishIngredientDetailResource]):
    results: List[DishIngredientDetailResource]

    @classmethod
    async def from_dish(
        cls,
        transaction: dal.TransactionManager,
        dish_id: int,
        request_url: str,
        params: DishIngredientQueryParams,
    ) -> "DishIngredientListView":
        t = transaction.get_table("dish_ingredient")
        dish = transaction.get_table("dish")
        ingredient = transaction.get_table("ingredient")
        ingredient_in_inventory = transaction.get_table("ingredient_in_inventory")
        stmt = (
            sa.select(
                t.c.id,
                t.c.dish_id,
                dish.c.name.label("dish_name"),
                t.c.ingredient_id,
                ingredient.c.name.label("ingredient_name"),
                t.c.quantity,
                t.c.unit,
                dish.c.created_on.label("used_on"),
                sa_total_count(t.c.id),
            )
            .select_from(
                t.join(dish, t.c.dish_id == dish.c.id)
                .join(
                    ingredient_in_inventory,
                    t.c.ingredient_id == ingredient_in_inventory.c.id,
                )
                .join(
                    ingredient,
                    ingredient.c.id == ingredient_in_inventory.c.ingredient_id,
                )
            )
            .where(t.c.dish_id == dish_id)
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
