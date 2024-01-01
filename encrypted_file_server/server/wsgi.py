# IMPORTS
import subprocess


# FUNCTIONS
def run():
    try:
        subprocess.run(
            ["gunicorn", "-w", "4", "-b", "0.0.0.0", "--log-level", "debug", "encrypted_file_server.server:app"]
        )
    except KeyboardInterrupt:
        print("Server stopped.")
