import itertools

class Puzzle(object):
	puzz = []
	rows = []
	def read(self, fn = 'human.txt'):
		with open(fn) as f:
			cs = []
			for n,l in enumerate(f.readlines()):
				if n < 9:
					cs.append(l[20:45])
				if n > 8:
					r = map(int, l[0:20].strip().split(' '))
					p = l[20:45]
					#  '.'' unknown   ' ' known blank, '#' known filled
					print "%50s >%25s<" % (str(r), p)
					assert all([x in ' .#' for x in p])
					self.puzz.append(p)
					self.rows.append(r)
			self.cols = [ [int(x) for x in y if x != ' '] for y in zip(*cs)]
			print 'rows: %s' % self.rows
			print 'cols: %s' % self.cols
	def __str__(self):
		return '\n'.join(x for x in p.puzz)

# generate candidates working from the clue first, by working out how many "free" spaces
# we have and the places they can go, e.g.
#  [3,1] onto .....  calculates ###a# with a being drawn from [(" ")]
#                               ### #      a   "   []
#
#  [3,1] onto ......            a###b#c with a,b,c drawn from [("", " ", " "), ("", "  ", ""), (" ", " ", "")]
#                              which simplies to
#                               a### b#c with a,b,c drawn from [(" ", "", ""), ("", " ", ""), ("", "", " ")]
#   [3,1] onto '......' is 3+1+1=5, so 1 'free' space, which can go before 3, after 3 or after the 1
#    ie, after block 0 or 1
#      The "n" free spaces are arranged into the integer partitions of n, restricted to having fewer items in
#      the partition than we have gaps. Any fewer items in the partition are made up with zeros, then use
#		combinations function to provide all the combinations
#
def partitions(n):
	# base case of recursion: zero is the sum of the empty list
	if n == 0:
		yield []
		return
	# modify partitions of n-1 to form partitions of n
	for p in partitions(n-1):
		yield [1] + p
		if p and (len(p) < 2 or p[1] > p[0]):
			yield [p[0] + 1] + p[1:]

def chk(got, expected):
	if not sorted(expected) == sorted(got):
		print("Failed, \n  expected: %s\n  got:      %s" % (expected, got))
		raise Exception("failed")

def candidates_clue(clue, puzzle):
	# how many free spaces?
	free_spaces = len(puzzle) - sum(clue) - (len(clue)-1)

	if free_spaces <= 0:
		# completely determined, return single solution
		ans = ' '.join(['#'*s for s in clue])
		assert len(ans) == len(puzzle)
		# print 'completely determined clue %s puzzle %s as %s' % (clue, puzzle, ans)
		return [ans]
	part = list(partitions(free_spaces))
	#print 'clue ' + str(clue) + ' puzzle ' + puzzle + ' free spaces: ' + str(free_spaces) + ", partitions: " + str(part)
	xs = []
	for p in part:
		if len(p) > len(clue)+1:
			#print ' skipping ' + str(p)
			continue
		if len(p) <= len(clue):
			p = p + [0]*(len(clue) - len(p) + 1)
		#print ' partition candidates: ' + str(p)
		seen = set()
		for x in itertools.permutations(p):
			if not x in seen:
				c = ' '*x[0] + ' '.join(['#'*c + ' '*s for c, s in zip(clue, x[1:]) ])
				# does c violate puzzle knowns?
				#print '  free_space arrangement ' + str(x) + ' gives ' + c
				if all( b == '.' or a == b for a,b in zip(c, puzzle)):
					xs.append(c)
				seen.add(x)
	return list(set(xs))

chk(list(partitions(1)), [[1]])
chk(list(partitions(2)), [[1,1], [2]])
chk(list(partitions(3)), [[1,1,1], [1,2], [3]])

candidates = candidates_clue
chk(candidates([3], '...'), ['###'])
chk(candidates([3], '.#.'), ['###'])
chk(candidates([2], '.#.'), ['## ', ' ##'])
chk(candidates([2], '...'), ['## ', ' ##'])
chk(candidates([1, 1], '...'), ['# #'])
chk(candidates([1], '. .'), ['#  ', '  #'])
chk(candidates([2], '....'), ['##  ', ' ## ', '  ##'])
chk(candidates([2,1], '....'), ['## #'])

chk(candidates([1, 3, 1, 3, 10, 2], '# ### # .##....#....##...'), ['# ### # ### ########## ##'])

p = Puzzle()
p.read(fn='input.txt')

def getRowPuzzle(p, n):
	return p.puzz[n]
def getColPuzzle(p, n):
	return ''.join(zip(*p.puzz)[n])
def putRowPuzzle(p, n, sol):
	p.puzz[n] = sol
def putColPuzzle(p, n, sol):
	trans = map(''.join, zip(*p.puzz))
	trans[n] = sol
	p.puzz =  map(''.join, zip(*trans))

unsolved = []
for n,x in enumerate(p.rows):
	unsolved.append( ('r', n, x, getRowPuzzle, putRowPuzzle) )
for n,y in enumerate(p.cols):
	unsolved.append( ('c', n, y, getColPuzzle, putColPuzzle) )

print 'Starting'
h = 0
while unsolved:
	rc, n, clue, statefn, updatefn = unsolved.pop(0)
	h += 1
	state = statefn(p, n)
	print 'Clue ' + str(clue) + ' state ' + str(state)
	c = candidates(clue, state)
	if len(c) == 1:
		updatefn(p, n, c[0])
		print 'Solved %s %d - puzzle now' % (rc, n)
		print(p)
		h = 0
	elif len(c) == 0:
		raise Exception("Unsatisfied " + str(clue) + " " + str(state))
	else:
		print '  %d solutions remain for %s %d, checking common values' % (len(c), rc, n)
		infers = 0
		state_next = list(state)
		for i in range(len(state)):
			if state[i] == '.':
				v = set([ci[i] for ci in c])
				if len(v) == 1:
					state_next[i] = c[0][i]
					infers += 1
		if infers > 1:
			updatefn(p, n, ''.join(state_next))
			print ' Did partial solve in %d positions for %s %d - puzzle now' % (infers, rc, n)
			print '   from clue ' + str(clue) + ' state ' + state + " -> " + ''.join(state_next)
			print(p)
			h = 0
		unsolved.append( (rc, n, clue, statefn, updatefn) )
	if h > 52:
		raise Exception('No iterative progress')

print '\n *** Solved ***'
print(p)
