# IMPORTS
from argparse import ArgumentParser

from encrypted_file_server.cli import start_server, add_new_user


# MAIN FUNCTIONS
def main():
    parser = ArgumentParser(
        prog="excelsior",
        description="an encrypted file server"
    )
    parser.add_argument("command", help="the command to run", choices=["start-server", "add-user"])
    args = parser.parse_args()

    if args.command == "start-server":
        start_server.run()
    else:  # Add user
        add_new_user.add_new_user()


if __name__ == "__main__":
    main()
