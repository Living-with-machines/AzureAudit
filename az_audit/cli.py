import sys
import argparse

from .storage import main as audit_storage


def parse_args(args):
    DESCRIPTION = "A Python CLI to audit Azure Storage Accounts"
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        "subscription",
        type=str,
        help="""The Azure subscription to audit. This can be either the
        subscription name or ID (hex-string). If providing the subscription
        name and it contains spaces, it must be wrapped in double-quotes.""",
    )

    return parser.parse_args()


def main():
    """Main function"""
    args = parse_args(sys.argv[1:])

    audit_storage(args.subscription)
