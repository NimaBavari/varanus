import time
from datetime import datetime, timedelta
from queue import Empty, Queue
from threading import Event, Thread
from typing import List

from config import resources
from lg import logger
from task import Task, handle_task

stop_event = Event()
task_queue = Queue()


def scheduler() -> None:
    """Scheduler thread that adds tasks to the queue based on their periods."""
    try:
        dynamic_times = [{"next_exec": datetime.now() + timedelta(seconds=res["period"]), **res} for res in resources]
        while not stop_event.is_set():
            now = datetime.now()
            soonest = min(dynamic_times, key=lambda url: url["next_exec"])
            if now >= soonest["next_exec"]:
                task = Task(handle_task, soonest["url"], soonest.get("pattern"))
                task_queue.put(task)

                soonest["next_exec"] += timedelta(seconds=soonest["period"])
            else:
                sleep_time = min((soonest["next_exec"] - now).total_seconds(), 1.0)
                if sleep_time > 0:
                    stop_event.wait(timeout=sleep_time)
    except Exception as e:
        logger.critical("Scheduler thread crashed: %s" % e)
        raise


def worker(worker_id: int) -> None:
    """Worker thread that processes tasks from the queue."""
    try:
        while not stop_event.is_set():
            try:
                task = task_queue.get(timeout=1.0)
                task.execute()
                task_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error("Worker %d failed to process task: %s" % (worker_id, e))
    except Exception as e:
        logger.critical("Worker %d thread crashed: %s" % (worker_id, e))
        raise


def start_workers(num_workers: int = 3) -> List[Thread]:
    """Starts multiple worker threads for parallel task processing."""
    workers = []
    for i in range(num_workers):
        worker_thread = Thread(target=worker, args=(i,), daemon=True)
        worker_thread.start()
        workers.append(worker_thread)

    return workers


if __name__ == "__main__":
    print("Starting monitoring daemon...")

    scheduler_thread = Thread(target=scheduler, daemon=True)
    scheduler_thread.start()

    worker_threads = start_workers()
    try:
        print("Daemon started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown signal received...")
        stop_event.set()

        print("Waiting for threads to stop...")
        scheduler_thread.join(timeout=5)

        for worker_thread in worker_threads:
            worker_thread.join(timeout=5)

        print("Shutdown complete.")
