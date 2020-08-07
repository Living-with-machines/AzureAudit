import os
import json
import getpass
import datetime
import warnings
import subprocess
from typing import Tuple
from itertools import compress

RG_KEYWORDS = ["cloud-shell", "play", "exper", "learn"]


def create_timestamp(timedelta_minutes: int = 30) -> str:
    """Creates a Unix-based timestamp for timedelta_minutes in the future.
    Used for generated SAS tokens with a short, finite lifetime.

    Args:
        timedelta_minutes (int, optional): Number of minutes in the future to
                                           generate the timestamp for.
                                           Defaults to 30.

    Returns:
        str: Unix-based timestamp
    """
    future = datetime.datetime.utcnow() + datetime.timedelta(minutes=timedelta_minutes)
    timestamp = future.isoformat(timespec="minutes")
    return timestamp + "Z"


def run_cmd(cmd: list) -> dict:
    """Run a command in a subshell

    Args:
        cmd (list): Command to be run broken up into list elements

    Returns:
        dict: The result of the command
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    msgs = proc.communicate()

    result = {
        "returncode": proc.returncode,
        "output": msgs[0].decode("utf8").strip("\n"),
        "err_msg": msgs[1].decode("utf8").strip("\n"),
    }

    if result["returncode"] != 0:
        raise Exception(result["err_msg"])

    return result


def construct_cmd(type: str) -> list:
    """Construct an Azure command to interact with storage services, containers
    and objects

    Args:
        type (str): The type of storage we would like to interact with.
                    Choices are: 'container' 'blob' 'share' 'file'

    Returns:
        list: The Azure command to be executed
    """
    # Check input
    valid_types = ["container", "blob", "share", "file"]
    if type not in valid_types:
        raise ValueError(
            f"Type {type} is not a valid input. Please provide one of the following inputs: {valid_types}"
        )

    return ["az", "storage", type, "list", "--query", "[*].name", "-o", "tsv"]


def login() -> None:
    """Login to Azure account and set active subscription."""
    print("Please prove the login credentials to your Turing Azure account")

    if "EMAIL" in os.environ:
        email = os.environ["EMAIL"]
    else:
        email = input("User email: ")

    password = getpass.getpass(prompt="Password: ")

    login_cmd = ["az", "login", "-u", email, "-p", password, "-o", "none"]
    run_cmd(login_cmd)
    print("Successfully logged into Azure")

    subscription = input("Please provide a subscription name or hex-string: ")

    sub_cmd = ["az", "account", "set", "-s", f"{subscription}"]
    run_cmd(sub_cmd)
    print(f"Successfully activated subscription: {subscription}")


def list_all_storage_accounts() -> list:
    """List all the storage accounts within the selected subscription

    Returns:
        list: A list containing dictionary all the storage accounts, their IDs
              and whether they contain blob, file, queue or table containers in
              a given subscription
    """
    list_cmd = ["az", "storage", "account", "list", "-o", "json"]
    result = run_cmd(list_cmd)
    data = json.loads(result["output"])

    accounts = []
    for item in data:
        selector = [keyword not in item["resourceGroup"] for keyword in RG_KEYWORDS]

        if all(selector):
            entry = {"name": item["name"], "id": item["id"]}

            for type in ["blob", "file", "queue", "table"]:
                entry[type] = (
                    item["encryption"]["services"][type]
                    if item["encryption"]["services"][type] is None
                    else item["encryption"]["services"][type]["enabled"]
                )

            accounts.append(entry)

    return sorted(accounts, key=lambda i: i["name"])


def generate_sas_token(account: dict) -> str:
    """Generate a SAS token for a storage account

    Args:
        account (dict): A dictionary containing basic info for the account

    Returns:
        str: The generated SAS token
    """
    expiry = create_timestamp()

    possible_services = ["b", "f", "q", "t"]
    exists = [account["blob"], account["file"], account["queue"], account["table"]]
    services = "".join(list(compress(possible_services, exists)))

    generate_cmd = [
        "az",
        "storage",
        "account",
        "generate-sas",
        "--expiry",
        expiry,
        "--permissions",
        "l",  # List permissions only
        "--resource-types",
        "cos",  # Permissions for Container, Object and Service types
        "--services",
        services,
        "--ids",
        account["id"],
        "-o",
        "tsv",
    ]

    result = run_cmd(generate_cmd)

    return result["output"]


def get_objects(account_name: str, sas_token: str, type: str) -> dict:
    """Get all containers and objects of a given type within a given storage
    account. Permissions granted with a SAS token.

    Args:
        account_name (str): The storage account to be searched
        sas_token (str): A SAS token
        type (str): The type of storage. Choices are 'container' 'blob' 'share'
                    'file'.

    Returns:
        dict: Keys are either container or share names, values are lists of
              either blob or file names.
    """
    cmd = construct_cmd(type)
    cmd.extend(["--account-name", account_name, "--sas-token", sas_token])
    result = run_cmd(cmd)

    if "\t" in result["output"]:
        tmp_pulled = result["output"].split("\t")
    elif "\n" in result["output"]:
        tmp_pulled = result["output"].split("\n")
    else:
        tmp_pulled = [result["output"]]

    pulled = [i for i in tmp_pulled if i != ""]

    if len(pulled) == 0:
        return None

    objects = {}
    if type == "container":
        cmd = construct_cmd("blob")
        cmd.extend(
            [
                "--account-name",
                account_name,
                "--sas-token",
                sas_token,
                "--container-name",
            ]
        )
    elif type == "share":
        cmd = construct_cmd("file")
        cmd.extend(
            ["--account-name", account_name, "--sas-token", sas_token, "--share-name"]
        )

    for object in pulled:
        result = run_cmd(cmd + [object])

        if "\t" in result["output"]:
            tmp_pulled = result["output"].split("\t")
        elif "\n" in result["output"]:
            tmp_pulled = result["output"].split("\n")
        else:
            tmp_pulled = [result["output"]]

        objects[object] = [i for i in tmp_pulled if tmp_pulled != ""]

    return objects


def list_objects(account: dict) -> Tuple[dict, dict]:
    """List the objects stored in the different storage file types

    Args:
        account (dict): Description of the storage account to search

    Returns:
        Tuple[dict, dict]: Returns the blobs and files stored in the account
    """
    sas = generate_sas_token(account)

    if account["blob"]:
        # Get blob containers and objects
        blobs = get_objects(account["name"], sas, "container")

    if account["file"]:
        # Get file objects
        files = get_objects(account["name"], sas, "share")

    if account["queue"] or account["table"]:
        # TODO: Implement table and queue storage listing
        warnings.warn(
            "Not Implemented: The code to access queue or table type storage is currently not implemented"
        )

    return blobs, files


def main():
    """Main function"""
    login()
    accounts = list_all_storage_accounts()
    print(f"Number of storage accounts: {len(accounts)}")

    contents = {"blobs": {}, "files": {}}
    for account in accounts:
        print("Account name:", account["name"])
        blobs, files = list_objects(account)

        if blobs is not None:
            contents["blobs"] = {**contents["blobs"], **blobs}

        if files is not None:
            contents["files"] = {**contents["files"], **files}

        # TODO: How to pretty print ``contents`` so it's readable and useful?


if __name__ == "__main__":
    main()
