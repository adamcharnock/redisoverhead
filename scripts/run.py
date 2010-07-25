
from redisoverhead import Overheads
from redis import Redis

redis = Redis(db=9)

# print Overheads(redis).list_fitness([6, 2])
# print Overheads(redis).list_fitness([5, 3])
print Overheads(redis).calculate()