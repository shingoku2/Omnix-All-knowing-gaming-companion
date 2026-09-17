import asyncio
import time
import uuid
import shutil
from pathlib import Path
import json

from omnix.session_logger import get_session_logger, SessionEvent

def setup_benchmark_data(logger, profile_id, num_sessions, events_per_session):
    logger.logs_dir.mkdir(parents=True, exist_ok=True)
    for i in range(num_sessions):
        session_id = f"20240101_{100000+i}"
        events_data = []
        for j in range(events_per_session):
            events_data.append({
                "timestamp": f"2024-01-01T12:00:{j%60:02d}",
                "event_type": "test_event",
                "game_profile_id": profile_id,
                "content": f"test content {j}",
                "meta": {}
            })

        file_path = logger.logs_dir / f"{profile_id}_{session_id}.json"
        with open(file_path, "w") as f:
            json.dump({
                "game_profile_id": profile_id,
                "session_id": session_id,
                "events": events_data
            }, f)

def run_benchmark():
    logger = get_session_logger()
    old_dir = logger.logs_dir
    test_dir = Path("/tmp/omnix_bench_logs")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    logger.logs_dir = test_dir

    profile_id = f"bench_profile_{uuid.uuid4().hex[:8]}"
    setup_benchmark_data(logger, profile_id, 10, 100)

    # Empty cache first
    logger.events.clear()
    logger._historical_sessions_cache.clear()

    start_time = time.time()
    logger.get_recent_events(profile_id, limit=500)
    end_time = time.time()
    print(f"Cold start (with file reading): {(end_time - start_time) * 1000:.2f} ms")

    # Now it's cached
    logger.events.clear()
    start_time = time.time()
    logger.get_recent_events(profile_id, limit=500)
    end_time = time.time()
    print(f"Warm start (cached): {(end_time - start_time) * 1000:.2f} ms")

    shutil.rmtree(test_dir)
    logger.logs_dir = old_dir

if __name__ == "__main__":
    run_benchmark()
