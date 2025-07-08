import yaml
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "role_matrix.yml"

def load_permissions():
    if FIXTURE_PATH.exists():
        with open(FIXTURE_PATH) as f:
            return yaml.safe_load(f)
    return {
        "Admin": [
            "auth.add_user",
            "auth.change_user",
            "auth.delete_user",
            "auth.view_user",
        ],
        "Manager": [
            "auth.add_user",
            "auth.change_user",
            "auth.view_user",
        ],
        "Staff": [
            "auth.view_user",
        ],
        "Read-Only": [],
    }


GROUP_PERMISSIONS = load_permissions()
