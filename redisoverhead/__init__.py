import math

from pyevolve import G1DList, GSimpleGA, Scaling, Selectors

def eval_polynomial(x, *coefficients):
	result = 0
	for exponent, coeff in enumerate(coefficients):
		coeff = coeff / 10.0
		result += coeff*x**exponent
	
	return result 

class Overheads(object):
	"""Calculating Reids overheads"""
	
	def __init__(self, redis):
		super(Overheads, self).__init__()
		self.redis = redis
		self.test_sizes = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 75, 100, 250, 500, 1000, 5000]
		self.redis_sizes = {
			"list": [],
			"set": [],
			"zset": [],
			"hash": [],
		}
		self.redis_funcs = {
			"list": lambda n: self.redis.rpush("_l", 1),
			"set": lambda n: self.redis.sadd("_s", n),
			"zset": lambda n: self.redis.zadd("_z", n, n),
			"hash": lambda n: self.redis.hset("_h", str(n), 1)
		}
	
	def calculate(self):
		"""docstring for calculate"""
		self._load_redis_sizes()
		
		genome = G1DList.G1DList(3)
		genome.evaluator.set(lambda *args, **kwargs: self._list_fitness(*args, **kwargs))
		genome.setParams(rangemin=0, rangemax=100)
		ga = GSimpleGA.GSimpleGA(genome)
		ga.selector.set(Selectors.GRouletteWheel)
		ga.setPopulationSize(1000)
		ga.setGenerations(200)
		ga.getPopulation().scaleMethod.set(Scaling.SigmaTruncScaling)
		ga.evolve(freq_stats=10)
		
		print ga.bestIndividual()
	
	def _load_redis_sizes(self):
		for size in self.test_sizes:
			for type_ in self.redis_funcs:
				self.redis.flushdb()
				
				size_before = self.redis.info()["used_memory"]
				
				for n in xrange(0, size):
					self.redis_funcs[type_](n)
				memory_used = self.redis.info()["used_memory"] - size_before
				
				# print "%d & %s => %d" % (size, type_, memory_used)
				
				self.redis_sizes[type_].append(memory_used)
		
		print self.redis_sizes
	
	def _list_fitness(self, chromosome):
		
		a, b, c = chromosome
		
		score = 0.0
		for k, size in enumerate(self.test_sizes):
			expected = self.redis_sizes["list"][k]
			# denominator = scale * math.log(size, base)
			# actual = (1/denominator) if denominator else 2**32
			
			# actual = c + (multi) * (1.0 / math.log(size + 1))
			# actual = eval_polynomial(size, *chromosome)
			actual = a + size*c + math.exp(size/(b*100 + 1))
			
			score += abs(actual - expected)
		
		score = -score
		return score
	



class Results(object):
	"""docstring for Results"""
	def __init__(self, key, list, set, zset, hash):
		super(Results, self).__init__()



