from redis import Redis, ConnectionPool

redis = Redis(
    connection_pool=ConnectionPool(
        host='47.238.165.188',
        password='cedlf@ddddsGDEl3df.3',
        port=6379,
        db=0,
        max_connections=10,
        decode_responses=True,
     )
)