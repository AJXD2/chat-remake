from pathlib import Path
import time
import subprocess
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.run = [
            "pipenv",
            "run",
            "python",
            "serv.py",
        ]  # Adjust the command to run your server script
        self.server_process = None
        self.recreate()

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type in ["created", "modified", "deleted"]:
            print(f"Changes detected in {event.src_path}, restarting serv.py...")
            self.recreate()

    def recreate(self):
        # Terminate the server process if it's running
        if self.server_process and self.server_process.poll() is None:
            # print("Terminating the previous server process...")
            self.server_process.terminate()
            self.server_process.wait()  # Wait for the process to terminate completely
            print("Previous server process terminated.")

        # Start a new server process and capture its output
        # print("Starting the server process...")
        self.server_process = subprocess.Popen(
            self.run,
            cwd=Path(".").absolute(),
            shell=True,  # Use shell=True for pipenv commands
        )
        print("New server process started.")

        # Print the PID of the new server process for debugging purposes
        # print("PID of the new server process:", self.server_process.pid)

        # Read and print the output from the server process


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path="server", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
