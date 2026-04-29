# Project Creation Runbook

This script automates the end-to-end provisioning of a new Azure DevOps project.

## Prerequisites

- Python 3.11+
- `ado_api` package installed and configured.
- Environment variables:
  - `org_name`: Your Azure DevOps organization name.
  - `pat`: Your Personal Access Token.

## Usage

```bash
python runbook/create_project.py \
  --project_name "MyNewProject" \
  --repo_name "MyNewRepo" \
  --pipeline_name "MainPipeline" \
  --email "user@example.com"
```

## Workflow Steps

1. Check if the project already exists (exists silently if it does).
2. Check if project and repository names are identical (exists silently if they are).
3. Create the project.
4. Create the repository.
5. Set repository capacity.
6. Fetch the `azure-pipelines.yml` template from `john19960810/test`.
7. Push the YAML template to the new repository's `main` branch.
8. Create an Azure Pipeline based on the YAML file.
9. Create `develop`, `uat`, `master`, and `hotfix` branches from `main`.
10. Apply branch policies to the new branches.
11. Add the specified user to `ProjectManager` and `ProjectMember` groups.
