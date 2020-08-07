import pytest
from freezegun import freeze_time

from az_audit.helper_functions import construct_cmd, create_timestamp, run_cmd


def test_construct_cmd():
    test1 = construct_cmd("container")
    test2 = construct_cmd("blob")
    test3 = construct_cmd("share")
    test4 = construct_cmd("file")

    assert test1 == ["az", "storage", "container", "list", "--query", "[*].name", "-o", "tsv"]
    assert test2 == ["az", "storage", "blob", "list", "--query", "[*].name", "-o", "tsv"]
    assert test3 == ["az", "storage", "share", "list", "--query", "[*].name", "-o", "tsv"]
    assert test4 == ["az", "storage", "file", "list", "--query", "[*].name", "-o", "tsv"]

    with pytest.raises(ValueError):
        construct_cmd("banana")


@freeze_time("2020-08-07 15:26:00")
def test_create_timestamp():
    stamp = create_timestamp()

    assert stamp == "2020-08-07T15:56Z"


def test_run_cmd():
    result = run_cmd(["echo", "hello"])

    assert result["returncode"] == 0
    assert result["output"] == "hello"
    assert result["err_msg"] == ""

    with pytest.raises(FileNotFoundError):
        run_cmd(["ehco", "hello"])
