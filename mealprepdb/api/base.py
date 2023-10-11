from typing import Generic, Optional, TypeVar, Annotated, Dict, Any
import abc

import pydantic
import orjson
from fastapi import FastAPI, HTTPException
import dataclasses
from starlette.datastructures import URLPath

from aiodal.oqm.views import Paginateable as _AiodalPaginateable
import enum
from aiodal import dal
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa


def orjson_serializer(obj: object) -> str:
    """Override internal serializer to handle numpy

    Args:
        obj (object): Any obj

    Returns:
        str: serialized string
    """
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY).decode()


# NOTE this is an abstract namespace
class BaseListViewQueryParamsModel:
    ...


ListViewQueryParamsT = TypeVar(
    "ListViewQueryParamsT", bound=BaseListViewQueryParamsModel
)


# This replaces `IdFilter`
class ObjectIdFromUrl:
    def __init__(self, obj_id: int):
        self.obj_id = obj_id


# NOTE this is needed so we can wrap subclasses in dataclass API
@dataclasses.dataclass
class Paginateable(_AiodalPaginateable):  # type: ignore [type-arg]
    total_count: int = 0


class HyperModel(pydantic.BaseModel):
    _fastapi: Optional[FastAPI] = pydantic.PrivateAttr()

    @classmethod
    def init_app(cls, app: FastAPI) -> None:
        cls._fastapi = app


class BaseFormModel(pydantic.BaseModel, abc.ABC):
    ...


class ResourceModel(HyperModel, abc.ABC):
    """Base class for all outgoing resources."""

    model_config = pydantic.ConfigDict(from_attributes=True)


ResourceModelT = TypeVar("ResourceModelT", bound=ResourceModel)
ResourceUri = Annotated[str, URLPath]


class ParentResourceModel(ResourceModel):
    """Base class for all outgoing parent resources."""

    @pydantic.computed_field  # type: ignore[misc]
    @property
    def links(self) -> Optional[Dict[str, ResourceUri]]:  # override in child class
        return None


class ListViewModel(pydantic.BaseModel, abc.ABC, Generic[ResourceModelT]):
    """Base class for all outgoing list views"""

    next_url: Optional[str] = None
    total_count: int = 0
    results: list[ResourceModelT]

    model_config = pydantic.ConfigDict(from_attributes=True)


# enums


# may need to work on this later
class IngredientTypeEnum(str, enum.Enum):
    meat = "meat"
    vegetable = "vegetable"
    starch = "starch"  # rice, flour, cornstarch
    herb = "herb"
    spice = "spice"  # cumin, bought spice, homemade spice mix (composed)
    seeds = "seeds"  # pumbkin, sesame, sunflower
    nuts = "nuts"  # almonds
    legumes = "legumes"  # beannsss
    fruit = "fruit"  # blueberries
    base_vegetable = "base_vegetable"  # onion, garlic, ginger
    sauce_broth = "sauce_broth"  # store bought
    seasonings = "seasonings"  # soy sauce, cooking wine, salt
    dairy = "dairy"
    _default = ""


class MealTypeEnum(str, enum.Enum):
    lunch = "lunch"
    breakfast = "breakfast"
    dinner = "dinner"
    dessert = "dessert"
    snack = "snack"
    _default = ""


# here for now
async def create(
    transaction: dal.TransactionManager, tablename: str, form_data: Dict[str, Any]
) -> sa.Row[Any]:
    """create method"""
    t = transaction.get_table(tablename)
    data = {
        **form_data,
    }

    stmt = sa.insert(t).values(data).returning(t)

    try:
        res = await transaction.execute(stmt)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict.")

    return res.one()


async def update(
    transaction: dal.TransactionManager,
    tablename: str,
    obj_id: int,
    form_data: Dict[str, Any],
) -> sa.Row[Any]:
    t = transaction.get_table(tablename)
    stmt = (
        sa.update(t)
        .values(
            {
                **form_data,
            }
        )
        .where(t.c.id == obj_id)
    ).returning(t)

    try:
        res = await transaction.execute(stmt)

    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict.")

    result = res.one_or_none()
    if not result:
        raise HTTPException(status_code=409, detail="Stale Data.")

    return result
