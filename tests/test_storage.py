import pytest
from unittest.mock import call, patch

from az_audit.storage import generate_sas_token, get_objects, list_all_storage_accounts


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


def test_generate_sas_token():
    test_account = {
        "name": "teststorage",
        "id": "test_id",
        "blob": True,
        "file": True,
        "queue": None,
        "table": None,
    }

    mock_time = patch(
        "az_audit.storage.create_timestamp", return_value="2020-0807T16:45Z"
    )
    mock_run = patch(
        "az_audit.storage.run_cmd",
        return_value={"returncode": 0, "output": "this_is_a_sas_token"},
    )

    expected_call = call(
        [
            "az",
            "storage",
            "account",
            "generate-sas",
            "--expiry",
            "2020-0807T16:45Z",
            "--permissions",
            "l",  # List permissions only
            "--resource-types",
            "cos",  # Permissions for Container, Object and Service types
            "--services",
            "bf",
            "--ids",
            "test_id",
            "-o",
            "tsv",
        ]
    )

    with mock_time as mock1, mock_run as mock2:
        output = generate_sas_token(test_account)

        mock1.assert_called_once()
        mock2.assert_called_once()
        assert mock2.call_args == expected_call
        assert output == "this_is_a_sas_token"


@patch("az_audit.storage.run_cmd", return_value={"returncode": 0, "output": ""})
def test_get_objects_short(mock):
    account_name = "test_account"
    sas_token = "this_is_a_sas_token"

    output = get_objects(account_name, sas_token, "container")

    mock.assert_called_once()
    assert output is None


@patch("az_audit.storage.run_cmd")
def test_get_objects_long_tabs(mock):
    account_name = "test_account"
    sas_token = "this_is_a_sas_token"

    mock.side_effect = [
        {"returncode": 0, "output": "container1\tcontainer2"},
        {"returncode": 0, "output": "blob1\tblob2"},
        {"returncode": 0, "output": "blob3\tblob4"},
    ]

    output = get_objects(account_name, sas_token, "container")

    assert mock.call_count == 3
    assert output == {
        "container1": ["blob1", "blob2"],
        "container2": ["blob3", "blob4"],
    }


@patch("az_audit.storage.run_cmd")
def test_get_objects_long_newlines(mock):
    account_name = "test_account"
    sas_token = "this_is_a_sas_token"

    mock.side_effect = [
        {"returncode": 0, "output": "share1\nshare2"},
        {"returncode": 0, "output": "file1\nfile2"},
        {"returncode": 0, "output": "file3"},
    ]

    output = get_objects(account_name, sas_token, "share")

    assert mock.call_count == 3
    assert output == {
        "share1": ["file1", "file2"],
        "share2": ["file3"],
    }
