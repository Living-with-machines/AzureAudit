import os
import getpass
from .helper_functions import run_cmd


def login(subscription: str) -> None:
    """Login to Azure account and set active subscription.

    Args:
        subscription (str): The Azure subscription to audit
    """
    print("Please provide the login credentials to your Azure account")

    if "EMAIL" in os.environ:
        email = os.environ["EMAIL"]
    else:
        email = input("User email: ")

    password = getpass.getpass(prompt="Password: ")

    login_cmd = ["az", "login", "-u", email, "-p", password, "-o", "none"]
    run_cmd(login_cmd)
    print("Successfully logged into Azure")

    sub_cmd = ["az", "account", "set", "-s", f"{subscription}"]
    run_cmd(sub_cmd)
    print(f"Successfully activated subscription: {subscription}")
