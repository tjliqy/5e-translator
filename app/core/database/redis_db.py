import redis   # 导入redis 模块

redis_pool = redis.ConnectionPool(
    host='localhost', port=6379, decode_responses=True)


class RedisDB:
    def __init__(self, db=0) -> (None):
        self.db_id = db
        self.r = redis.StrictRedis(connection_pool=redis_pool, db=db)

    def put(self, key: str, value: str, tag="") -> (bool):
        tag_v = "%" + value
        if tag is not None and tag!= "":
            tag_v = tag + tag_v
        return self.r.sadd(key, tag_v)

    def get(self, key: str, tag="") -> (list[str]):
        value = self.r.sinter(key)
        if value == None or len(value) == 0:
            return []
        if tag == None or tag == "":
            return [v[v.find('%')+1:] for v in value]
        else:
            # print(tag, value)
            tag_v = [v[v.find('%')+1:] for v in value if v.startswith(tag)]
            if len(tag_v) > 0:
                return tag_v
            return [v[v.find('%')+1:] for v in value]
    # def update(self, key: str, value: str, tag="") -> (bool):
    #     tag_k = key
    #     if tag != "":
    #         tag_k = key + "%" + tag
    #     return self.r.set(tag_k, value)

    def keys(self):
        all_keys = self.r.keys()
        return all_keys
    def clean(self):
        self.r.flushdb()
