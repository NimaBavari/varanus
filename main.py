import time
from datetime import datetime, timedelta
from queue import Queue
from threading import Event, Lock, Thread

from config import resources
from task import Task, handle_task

task_queue = Queue()
queue_lock = Lock()


def scheduler() -> None:
    dynamic_times = [{"next_exec": datetime.now() + timedelta(seconds=res["period"]), **res} for res in resources]
    while True:
        soonest = min(dynamic_times, key=lambda url: url["next_exec"])
        if datetime.now() >= soonest["next_exec"]:
            task = Task(handle_task, soonest["url"], soonest.get("pattern"))
            with queue_lock:
                task_queue.put(task)

            soonest["next_exec"] += timedelta(seconds=soonest["period"])


def worker() -> None:
    while True:
        with queue_lock:
            if not task_queue.empty():
                task = task_queue.get()
                task.execute()
            else:
                time.sleep(0.1)  # NOTE: avoids busy-waiting for efficient CPU usage


if __name__ == "__main__":
    scheduler_thread = Thread(target=scheduler, daemon=True)
    scheduler_thread.start()

    worker_thread = Thread(target=worker, daemon=True)
    worker_thread.start()

    stop_event = Event()
    try:
        while True:
            stop_event.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
