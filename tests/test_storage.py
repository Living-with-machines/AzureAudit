import pytest
from unittest.mock import call, patch

from az_audit.storage import list_all_storage_accounts


@patch(
    "az_audit.storage.run_cmd",
    return_value={
        "returncode": 0,
        "output": '[{"resourceGroup": "cloud-shell-storage"}, {"resourceGroup": "playground"}, {"resourceGroup": "experimental"}, {"resourceGroup": "learnazure"}, {"resourceGroup": "res_grp", "name": "storageaccount", "id": "some_id", "encryption": {"services": {"blob": {"enabled": true}, "file": {"enabled": true}, "queue": null, "table": null}}}]',
        "err_msg": "",
    },
)
def test_list_all_storage_accounts(mock):
    output = list_all_storage_accounts()

    mock.assert_called_once()
    mock.assert_called_once_with(["az", "storage", "account", "list", "-o", "json"])

    assert output == [
        {
            "name": "storageaccount",
            "id": "some_id",
            "blob": True,
            "file": True,
            "queue": None,
            "table": None,
        }
    ]
