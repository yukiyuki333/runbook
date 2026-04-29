"""
Azure DevOps Project Creation Runbook.

This script automates the creation of a new project, repository, pipeline,
branches, and group memberships in Azure DevOps using the ado_api package.
"""
import os
import sys
import argparse
import logging
from ado_api import project, repo, pipeline, branch, member

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main orchestration logic for project provisioning.
    """
    parser = argparse.ArgumentParser(description="Azure DevOps Project Creation Runbook")
    parser.add_argument("--project_name", required=True, help="Name of the Azure DevOps project")
    parser.add_argument("--repo_name", required=True, help="Name of the repository to create")
    parser.add_argument("--pipeline_name", required=True, help="Name of the pipeline to create")

    args = parser.parse_args()

    # Phase 2: Foundational - Environment Setup
    org_name = os.getenv("org_name")
    pat = os.getenv("pat")
    email = os.getenv("email")

    if not org_name or not pat:
        logger.error("Environment variables 'org_name' or 'pat' are missing.")
        sys.exit(1)

    project_name = args.project_name
    repo_name = args.repo_name
    pipeline_name = args.pipeline_name

    logger.info(f"Starting runbook for project: {project_name}")

    try:
        # Step 1: Check project exists
        if project.check_project_exists(org_name, project_name, pat):
            logger.info(f"Project '{project_name}' already exists. Exiting silently.")
            return

        # Step 2: Check project_name == repo_name
        if project_name == repo_name:
            logger.info("project_name and repo_name are identical. Exiting silently.")
            return

        # Step 3: Create project
        logger.info(f"Creating project: {project_name}")
        project.create_project(org_name, pat, project_name)

        # Step 4: Create ADO repo
        logger.info(f"Creating repository: {repo_name}")
        repo.create_ado_repo(org_name, project_name, repo_name, pat)

        # Step 5: Set Azure repo capacity
        logger.info(f"Setting repository capacity for: {repo_name}")
        repo.set_azure_repo_capacity(org_name, project_name, repo_name, pat)

        # Step 6: Get YAML template
        logger.info("Fetching YAML template from john19960810/test")
        yaml_template = repo.get_azure_repo_file(
            org_name, 'john19960810', 'test', '/azure-pipelines.yml', pat, branch='test'
        )

        # Step 7: Validate YAML template
        if not yaml_template:
            raise ValueError("YAML template is empty or could not be fetched.")

        # Step 8: Push YAML to repo
        logger.info(f"Pushing YAML template to {repo_name} main branch")
        success = repo.push_azure_repo_file(
            yaml_template, org_name, project_name, repo_name, '/azure-pipelines.yml', pat,
            branch='main', commit_message='Initial pipeline setup from template'
        )

        # Step 9: Validate push success
        if not success:
            raise ValueError("Failed to push YAML template to the repository.")

        # Step 10: Create Azure Pipeline
        logger.info(f"Creating Azure Pipeline: {pipeline_name}")
        pipeline_dict = pipeline.create_azure_pipeline_auto(
            org_name, project_name, repo_name, pipeline_name, '/azure-pipelines.yml', pat
        )

        # Step 11: Validate pipeline creation
        if not pipeline_dict:
            raise ValueError("Failed to create Azure Pipeline.")

        # Step 12: Create branches
        branches = ['develop', 'uat', 'master', 'hotfix']
        for target_branch in branches:
            logger.info(f"Creating branch: {target_branch}")
            create_branch_success = branch.create_branch(
                org_name, project_name, repo_name, pat, target_branch, 'main'
            )
            if not create_branch_success:
                raise ValueError(f"Failed to create branch: {target_branch}")

        # Step 13: Set branch policies
        for target_branch in branches:
            logger.info(f"Setting branch policy for: {target_branch}")
            branch.set_git_branch_policy(org_name, project_name, repo_name, target_branch, pat)

        # Step 14: Add member to groups
        groups = ['ProjectManager', 'ProjectMember']
        for group_name in groups:
            logger.info(f"Adding {email} to group: {group_name}")
            # Use get_group and update_group from member.py
            group_info = member.get_group(org_name, project_name, group_name, pat)
            if group_info:
                member.update_group(org_name, project_name, group_info['id'], email, pat)
            else:
                logger.warning(f"Group '{group_name}' not found. Skipping membership update.")

        logger.info("Runbook completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during provisioning: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
