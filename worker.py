# worker.py
import os
import sys
from redis import Redis
from rq import Worker, Queue

# Add project root so Python can find Classifier
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from Classifier import classifier_enricher

listen = ['crisislens']
redis_conn = Redis(host='localhost', port=6379, db=0)

if __name__ == '__main__':
    qs = list(map(lambda q: Queue(q, connection=redis_conn), listen))
    w = Worker(qs)
    w.work()
