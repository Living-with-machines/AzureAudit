import datetime
import subprocess


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
