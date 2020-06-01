import pyarrow as pa
import redis

redis_conf = {"host": "localhost", "port": 6379, "db": 0}

redis_pool = None


def init():
    global redis_pool
    print("PID %d: initializing redis pool..." % os.getpid())
    redis_pool = redis.ConnectionPool(
        host=redis_conf["host"], port=redis_conf["port"], db=redis_conf["db"]
    )


def cache_df(alias, df):

    cur = redis.Redis(connection_pool=redis_pool)
    context = pa.default_serialization_context()
    df_compressed = context.serialize(df).to_buffer().to_pybytes()

    res = cur.set(alias, df_compressed)
    if res == True:
        print("df cached")


def get_cached_df(alias):

    cur = redis.Redis(connection_pool=redis_pool)
    context = pa.default_serialization_context()
    all_keys = [key.decode("utf-8") for key in cur.keys()]

    if alias in all_keys:
        result = cur.get(alias)

        dataframe = pd.DataFrame.from_dict(context.deserialize(result))

        return dataframe

    return None
