from rq import Queue
from worker import conn

q = Queue(connection=conn)

from clock import load_rss, classify

result = q.enqueue(load_rss)
result = q.enqueue(classify)