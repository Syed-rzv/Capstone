# worker.py
import os
import sys
from redis import Redis
from rq import Worker, Queue, SimpleWorker

# Add Classifier to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the processing function
from Classifier.tasks import process_emergency_call

listen = ['crisislens']
redis_conn = Redis(host='localhost', port=6379, db=0)

if __name__ == '__main__':
    print("🚀 CrisisLens Worker Starting...")
    print(f"📡 Listening to queues: {listen}")
    print("-" * 60)
    
    qs = list(map(lambda q: Queue(q, connection=redis_conn), listen))
    # Use SimpleWorker instead of Worker for Windows compatibility
    w = SimpleWorker(qs, connection=redis_conn)
    w.work()