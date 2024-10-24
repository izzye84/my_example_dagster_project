# Using dbt with Dagster's hybrid deployment

1. **Project Setup**
   - Copy your dbt project into the root of your Dagster repository
   - Add `profiles.yml` to the root of your dbt project
   - Update the `profiles.yml` with the appropriate [`dbt adapter`](https://docs.getdbt.com/docs/supported-data-platforms) connection info
     - We recommend using environment variables—[see example configuration](https://github.com/dagster-io/hooli-data-eng-pipelines/blob/master/dbt_project/profiles.yml)

2. **Update Dependencies**
   - Add the following packages to your `setup.py`:
     - `dagster-dbt`
     - `dbt-<your_adapter>`
   - Add the following package_data config to the `setup.py`:

     ```python
     from setuptools import find_packages, setup

     setup(
         name="my_example_dagster_project",
         version="0.0.1",
         packages=find_packages(),
         package_data={
             "my-dagster-code-location": [
                 "dbt-project/**/*",
             ],
         },
         ...
     ```

3. **Configure the `dagster-dbt` (dbt Core) integration**
   - Create a `project.py` file with the following code to your existing code location:
  
     ```python
     from pathlib import Path

     from dagster_dbt import DbtProject
      
     my_dbt_project = DbtProject(
         project_dir=Path(__file__).joinpath("..", "..", "my_dbt_project").resolve(),
         packaged_project_dir=Path(__file__).joinpath("..", "dbt-project").resolve(),
     )
     my_dbt_project.prepare_if_dev()
     ```

   - Be sure to update the `project_dir` variable with your dbt project name

4. **Create dbt Assets**
   - Either:
     - Copy the provided `assets.py` file, or
    
     ```python
     from dagster import AssetExecutionContext
     from dagster_dbt import DbtCliResource, dbt_assets
    
     from .project import my_dbt_project
    
    
     @dbt_assets(manifest=my_dbt_project.manifest_path)
     def my_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
         yield from dbt.cli(["build"], context=context).stream()  
     ```
   
     - Add the `dbt_assets` code to an existing asset file
   - Ensure the dbt assets and resource are included with your other asset definitions:
  
     ```python
     from dagster import Definitions
     from dagster_dbt import DbtCliResource
     from .assets import my_dbt_assets
     from .project import my_dbt_project
     
     defs = Definitions(
         assets=[my_dbt_assets],
         resources={
             "dbt": DbtCliResource(project_dir=my_dbt_project),
         },
     )
     ```

5. **Update GitHub Action**
   - Add a "Prepare dbt project for deployment" step just before the "Build and upload Docker image" step:
     ```yaml
     - name: Prepare DBT project for deployment
        run: |
          python -m pip install pip --upgrade
          pip install . --upgrade --upgrade-strategy eager                                            ## Install the Python dependencies from the setup.py file, ex: dbt-core and dbt-duckdb
          dagster-dbt project prepare-and-package --file my_dagster_code_location/project.py          ## Replace with the project.py location in the Dagster project folder
        shell: bash 
     ```
   - Note: You'll need to add dbt variables/secrets in GitHub that correspond to the environment variables in your `profiles.yml`
     - These credentials are used to create the `manifest.json`

6. **Testing**
   - Test the dbt Core integration locally using `dagster dev`
   - If everything works as expected, open a Pull Request
