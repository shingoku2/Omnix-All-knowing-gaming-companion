import asyncio
import time
import uuid
import sys
import shutil
from pathlib import Path
import json

from omnix.session_logger import get_session_logger, SessionEvent

async def load_session_async(logger, game_profile_id, session_id):
    session_file = logger._get_session_file(game_profile_id, session_id)

    if not session_file.exists():
        return []

    # Using to_thread for file I/O to avoid blocking the event loop
    def _read_file():
        with open(session_file, "r") as f:
            return json.load(f)

    data = await asyncio.to_thread(_read_file)

    events = [SessionEvent.from_dict(e) for e in data.get("events", [])]
    return events

async def get_recent_events_async(logger, game_profile_id: str, limit: int = 50):
    events = logger.get_current_session_events(game_profile_id)

    if len(events) < limit:
        session_files = sorted(
            logger.logs_dir.glob(f"{game_profile_id}_*.json"), reverse=True
        )

        # Get sessions to load
        sessions_to_load = []
        for session_file in session_files[:5]:
            session_id = session_file.stem[len(game_profile_id) + 1 :]
            if session_id not in logger.current_sessions.values():
                sessions_to_load.append(session_id)

        # Load them concurrently
        if sessions_to_load:
            tasks = [load_session_async(logger, game_profile_id, sid) for sid in sessions_to_load]
            historical_events_lists = await asyncio.gather(*tasks)

            # They are sorted most recent first in `sessions_to_load`
            # We want chronological order (oldest first)
            for historical_events in reversed(historical_events_lists):
                events = historical_events + events

    return events[-limit:] if len(events) > limit else events

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

async def run_benchmark():
    logger = get_session_logger()

    old_dir = logger.logs_dir
    test_dir = Path("/tmp/omnix_bench_logs2")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    logger.logs_dir = test_dir

    profile_id = f"bench_profile_{uuid.uuid4().hex[:8]}"

    setup_benchmark_data(logger, profile_id, 100, 100)

    num_runs = 50
    start_time = time.time()

    for _ in range(num_runs):
        logger.events.clear()
        await get_recent_events_async(logger, profile_id, limit=500)

    end_time = time.time()
    avg_time = (end_time - start_time) / num_runs * 1000

    print(f"Average time per async get_recent_events (limit=500): {avg_time:.2f} ms")

    shutil.rmtree(test_dir)
    logger.logs_dir = old_dir

    return avg_time

if __name__ == "__main__":
    asyncio.run(run_benchmark())
