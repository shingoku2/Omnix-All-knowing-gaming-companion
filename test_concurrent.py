import concurrent.futures
from pathlib import Path
import json
import time

def worker(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

paths = [f"/tmp/omnix_bench_logs/bench_profile_*/20240101_{100000+i}.json" for i in range(5)]
# wait, glob it properly
import glob
paths = glob.glob("/tmp/omnix_bench_logs/*/*.json")[:5]

if paths:
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(worker, paths))
    print("Concurrent time:", (time.time() - start) * 1000, "ms")
