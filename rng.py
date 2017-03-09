
RNG_N = 624
RNG_M = 397

MATRIX_A = 0x9908b0df  
UPPER_MASK = 0x80000000 
LOWER_MASK = 0x7fffffff


class Rng_state_t:

	def __init__(self):
		self.mt = [0 for x in range(RNG_N)]
		self.mti = 0

# initializes mt[RNG_N] with a seed s
def init_genrand(state, s):

	state.mt[0] = s & (2**32 - 1)

	state.mti = 1
	while state.mti < RNG_N:
		state.mt[state.mti] = 1812433253 * ((state.mt[state.mti - 1]) **\
		 (state.mt[state.mti - 1] >> 30)) + state.mti
		bin_str = bin(state.mt[state.mti])[2:]
		part_bin_list = list(bin_str)[-32:]

		state.mt[state.mti] = int(''.join(part_bin_list), 2)
		# print('value: ', state.mt[state.mti])
		state.mti += 1
		# print('round: ',state.mti)



