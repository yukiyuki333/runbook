import os
import sys
from unittest.mock import patch
from ado_api.member import manage_group_membership

# Mock environment variables
os.environ["org_name"] = "mock-org"
os.environ["pat"] = "mock-pat"
os.environ["email"] = "test@example.com"

# Mock sys.argv
sys.argv = ["manage_membership.py", "MockProject", "add", "ProjectManager"]

# Input from Environment Variables and Runtime Parameters
org_name = os.getenv("org_name")
pat = os.getenv("pat")
email = os.getenv("email")

if len(sys.argv) < 3:
    print("Usage: python manage_membership.py <project_name> <action: add|remove> <group_type: ProjectManager|ProjectMember>")
    sys.exit(1)

project_name = sys.argv[1]
action = sys.argv[2]
group_type = sys.argv[3]

# Mock the underlying API calls to simulate success
with patch("ado_api.member.get_group") as mock_get, patch("ado_api.member.update_group") as mock_update:
    mock_get.return_value = "mock_descriptor"
    mock_update.return_value = True

    success = manage_group_membership(
        organization=org_name,
        project_name=project_name,
        user_email=email,
        group_type=group_type,
        action=action,
        pat=pat
    )

if success:
    print(f"Successfully {action}ed {email} to/from {group_type} in {project_name}")
else:
    print("Failed to manage group membership.")
