"""init schema

Revision ID: 15df77bde24b
Revises: 
Create Date: 2023-09-04 11:39:18.104020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "15df77bde24b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    id_column_big_autoincrementing = sa.Column(
        "id", sa.BigInteger, primary_key=True, autoincrement=True
    )

    id_column_autoincrementing = sa.Column(
        "id", sa.Integer, primary_key=True, autoincrement=True
    )

    updated_on = sa.Column(
        "updated_on",
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),  # type: ignore
    )
    created_on = sa.Column(
        "created_on",
        sa.Date(),
        server_default=sa.func.now(),
    )

    # this needs more thinking; where does eggs belong here?
    _ingredient_type_enum = [
        "meat",
        "vegetable",
        "starch",  # rice, flour, cornstarch
        "herb",
        "spice",  # cumin, bought spice, homemade spice mix (composed)
        "seeds",  # pumbkin, sesame, sunflower
        "nuts",  # almonds
        "legumes",  # beannsss
        "fruit",  # blueberries
        "base_vegetable",  # onion, garlic, ginger
        "sauce_broth",  # store bought
        "seasonings",  # soy sauce, cooking wine, salt
        "dairy",
    ]

    # this is more of a reference table
    op.create_table(
        "ingredient",
        id_column_autoincrementing,
        sa.Column("name", sa.String(255), unique=True),
        sa.Column(
            "type",
            sa.Enum(
                *_ingredient_type_enum,
                name="ingredienttype_cc",
                create_constraint=True,  # will this bite me back in the future?
                native_enum=False,
            ),
            nullable=True,
        ),
        updated_on,
    )

    op.create_table(
        "ingredient_in_inventory",
        id_column_big_autoincrementing,
        sa.Column(
            "ingredient_id",
            sa.BigInteger,
            sa.ForeignKey("ingredient.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_where", sa.String(255)),
        sa.Column("brand", sa.String(255)),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column("quantity", sa.Float, nullable=True),
        sa.Column("unit", sa.String(64), nullable=True),
        sa.Column(
            "purchased_on",
            sa.Date(),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "finished_on",
            sa.Date(),
            nullable=True,
        ),
        updated_on,
    )

    op.create_table(
        "dish",
        id_column_big_autoincrementing,
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "parent_dish_id",
            sa.BigInteger,
            sa.ForeignKey("dish.id", ondelete="SET NULL"),
            nullable=True,
        ),
        created_on,
        updated_on,
    )

    op.create_table(
        "dish_ingredient",
        id_column_big_autoincrementing,
        sa.Column(
            "dish_id",
            sa.BigInteger,
            sa.ForeignKey("dish.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ingredient_id",
            sa.BigInteger,
            sa.ForeignKey("ingredient_in_inventory.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Float, nullable=True),
        sa.Column("unit", sa.String(64), nullable=True),
        sa.UniqueConstraint("dish_id", "ingredient_id", name="uq__dish_ingredient"),
        updated_on,
    )

    _meal_type_enum = ["lunch", "breakfast", "dinner", "dessert", "snack"]
    op.create_table(
        "meal",
        id_column_big_autoincrementing,
        sa.Column(
            "type",
            sa.Enum(
                *_meal_type_enum,
                name="mealtype_cc",
                create_constraint=True,
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column("description", sa.String(255)),
        sa.Column(
            "consumed_on",
            sa.Date(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        updated_on,
    )

    op.create_table(
        "meal_dish",
        id_column_big_autoincrementing,
        sa.Column(
            "meal_id",
            sa.BigInteger,
            sa.ForeignKey("meal.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "dish_id",
            sa.BigInteger,
            sa.ForeignKey("dish.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "quantity", sa.Float, nullable=True
        ),  # how much of a dish went into a meal
        sa.Column("unit", sa.String(64), nullable=True),
        updated_on,
        sa.UniqueConstraint("dish_id", "meal_id", name="uq__meal_dish"),
    )

    op.create_table(
        "meal_ingredient",
        id_column_big_autoincrementing,
        sa.Column(
            "meal_id",
            sa.BigInteger,
            sa.ForeignKey("meal.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ingredient_id",
            sa.BigInteger,
            sa.ForeignKey("ingredient_in_inventory.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "quantity", sa.Float, nullable=True
        ),  # how much of a ingredient went into a meal
        sa.Column("unit", sa.String(64), nullable=True),
        updated_on,
        sa.UniqueConstraint("ingredient_id", "meal_id", name="uq__meal_ingredient"),
    )

    # ingredient
    op.create_index(
        "idx__ingredient_in_inventory__purchased_on",
        "ingredient_in_inventory",
        columns=["purchased_on"],
    )

    op.create_index(
        "idx__ingredient_in_inventory__ingredient_id_purchased_on",
        "ingredient_in_inventory",
        columns=["ingredient_id", "purchased_on"],
    )

    # meal indgrient
    op.create_index(
        "idx__meal_ingredient__meal_id",
        "meal_ingredient",
        columns=["meal_id"],
    )

    op.create_index(
        "idx__meal_ingredient__ingredient_id",
        "meal_ingredient",
        columns=["ingredient_id"],
    )

    op.create_index(
        "idx__meal_ingredient__meal_id_ingredient_id",
        "meal_ingredient",
        columns=["meal_id", "ingredient_id"],
    )

    # dish ingredient
    op.create_index(
        "idx__dish_ingredient__ingredient_id",
        "dish_ingredient",
        columns=["ingredient_id"],
    )

    op.create_index(
        "idx__dish_ingredient__dish_id",
        "dish_ingredient",
        columns=["dish_id"],
    )

    op.create_index(
        "idx__dish_ingredient__dish_id_ingredient_id",
        "dish_ingredient",
        columns=["dish_id", "ingredient_id"],
    )

    # dish
    op.create_index(
        "idx__dish__created_on",
        "dish",
        columns=["created_on"],
    )

    # meal
    op.create_index(
        "idx__meal__consumed_on",
        "meal",
        columns=["consumed_on"],
    )


def downgrade() -> None:
    op.drop_table("meal_ingredient")
    op.drop_table("meal_dish")
    op.drop_table("meal")
    op.drop_table("dish_ingredient")
    op.drop_table("dish")
    op.drop_table("ingredient_in_inventory")
    op.drop_table("ingredient")
