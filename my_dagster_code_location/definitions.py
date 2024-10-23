from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import my_dbt_assets
from .project import my_dbt_project
from .schedules import schedules

defs = Definitions(
    assets=[my_dbt_assets],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=my_dbt_project),
    },
)

