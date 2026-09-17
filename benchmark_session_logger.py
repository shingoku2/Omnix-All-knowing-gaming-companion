import asyncio
import time
import uuid
import sys
import shutil
from pathlib import Path
import json

from omnix.session_logger import get_session_logger, SessionEvent

def setup_benchmark_data(logger, profile_id, num_sessions, events_per_session):
    print(f"Setting up {num_sessions} sessions with {events_per_session} events each...")
    logger.logs_dir.mkdir(parents=True, exist_ok=True)

    # Create fake files
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

    # Store old logs dir to restore later if needed, but we'll use a custom one for test
    old_dir = logger.logs_dir
    test_dir = Path("/tmp/omnix_bench_logs")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    logger.logs_dir = test_dir

    profile_id = f"bench_profile_{uuid.uuid4().hex[:8]}"

    # The limit is large enough to fetch many events. We can read up to 5 files or more if changed.
    # To really stress test, let's create 100 sessions. And limit=500, but in current code it max reads 5 files anyway.
    # Note: Using valid seconds for the dummy timestamp so it doesn't fail from_dict.
    setup_benchmark_data(logger, profile_id, 100, 10) # 100 sessions, 10 events each

    # Clear memory cache so it relies entirely on disk loading for historical
    logger.events.clear()

    # Warmup
    logger.get_recent_events(profile_id, limit=50)

    # Benchmark
    num_runs = 50
    start_time = time.time()

    for _ in range(num_runs):
        logger.events.clear() # Force reload from disk
        logger.get_recent_events(profile_id, limit=50)

    end_time = time.time()
    avg_time = (end_time - start_time) / num_runs * 1000 # in ms

    print(f"Average time per get_recent_events (limit=50): {avg_time:.2f} ms")

    # Clean up
    shutil.rmtree(test_dir)
    logger.logs_dir = old_dir

    return avg_time

if __name__ == "__main__":
    run_benchmark()
