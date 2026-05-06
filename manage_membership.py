import os
import sys
import argparse
import logging
from ado_api import project, repo, pipeline, branch, member


def main():
    org_name = os.getenv("org_name")
    pat = os.getenv("pat")

    parser = argparse.ArgumentParser(description="Azure DevOps Project Creation Runbook")
    parser.add_argument("--update_member_flag", required=True, help="update_member_flag")
    parser.add_argument("--project_name", required=True, help="project_name")
    parser.add_argument("--email", required=True, help="Email")

    args = parser.parse_args()
    update_member_flag = args.update_member_flag
    project_name = args.project_name
    email = args.email

    if len(sys.argv) < 2:
        print("Usage: python manage_membership.py <project_name> <action: add|remove> <group_type: ProjectManager|ProjectMember>")
        sys.exit(1)

    groups = ['ProjectManager', 'ProjectMember']
    for group_name in groups:
        logger.info(f"Adding {email} to group: {group_name}")
        # Use get_group and update_group from member.py
        group_info = member.get_group(org_name, project_name, group_name, pat)
        if group_info:
            member.update_group(org_name, project_name, group_info['id'], email, update_member_flag, pat)
        else:
            logger.warning(f"Group '{group_name}' not found. Skipping membership update.")

    logger.info("Runbook completed successfully.")


if __name__=="main":
    main()