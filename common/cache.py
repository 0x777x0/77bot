from redis import Redis, ConnectionPool

redis = Redis(
    connection_pool=ConnectionPool(
        host='47.108.165.72',
        password='cedlf@ddddsGDEl3df.3',
        port=6379,
        db=0,
        max_connections=10,
        decode_responses=True,
     )
)

#  待会去看看