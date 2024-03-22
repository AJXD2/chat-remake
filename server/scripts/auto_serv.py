from pathlib import Path
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil


BASE = Path(__file__).parent.parent

# Command to start the server process using pipenv
SERVER_COMMAND = ["pipenv", "run", "python", "serv.py"]
# Directory to monitor for changes
MONITOR_DIRECTORY = BASE.joinpath("app")
# Port number used by the server
SERVER_PORT = 2000


class FileChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(f"Change detected: {event.event_type} - {event.src_path}")
        restart_server()


def start_server():
    print("Starting server...")
    subprocess.Popen(SERVER_COMMAND, cwd=BASE)


def find_process_by_port(port):
    for proc in psutil.net_connections():
        if proc.laddr.port == port:
            return proc.pid
    return None


def terminate_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process with PID {pid} terminated successfully.")
    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} not found.")


def restart_server():
    print("Restarting server...")
    # Find and terminate processes listening on the server port
    pid = find_process_by_port(SERVER_PORT)
    if pid is not None:
        terminate_process(pid)
    else:
        print(f"No process found using port {SERVER_PORT}.")

    # Start the server process again
    start_server()


def main():
    start_server()

    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIRECTORY, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
