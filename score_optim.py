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

precalc_part = [list(partitions(n)) for n in range(20)]

def candidates(clue, puzzle):
	# how many free spaces?
	free_spaces = len(puzzle) - sum(clue) - (len(clue)-1)
	if free_spaces == 0:
		# completely determined, return single solution
		ans = ' '.join(['#'*s for s in clue])
		assert len(ans) == len(puzzle)
		# print 'completely determined clue %s puzzle %s as %s' % (clue, puzzle, ans)
		yield ans
		return
	else:
		print '  t-clue ' + str(clue) + ' puzzle ' + puzzle + ' free spaces: ' + str(free_spaces)
		places_for_spaces = len(clue) + 1

		for p in precalc_part[free_spaces]:
			if len(p) > places_for_spaces:
				continue
			p = p + [0]*(places_for_spaces - len(p))
			print ' partition candidates: ' + str(p)
			seen = set() # partition can contain duplicates, filter them
			for x in itertools.permutations(p):
				if not x in seen:
					seen.add(x)
					c = ' '*x[0] + ' '.join(['#'*c + ' '*s for c, s in zip(clue, x[1:]) ])
					# does c violate puzzle knowns?
					#print '  free_space arrangement ' + str(x) + ' gives ' + c
					if all( b == '.' or a == b for a,b in zip(c, puzzle)):
						yield c

chk(list(partitions(1)), [[1]])
chk(list(partitions(2)), [[1,1], [2]])
chk(list(partitions(3)), [[1,1,1], [1,2], [3]])

chk(candidates([3], '...'), ['###'])
chk(candidates([3], '.#.'), ['###'])
chk(candidates([2], '.#.'), ['## ', ' ##'])
chk(candidates([2], '...'), ['## ', ' ##'])
chk(candidates([1, 1], '...'), ['# #'])
chk(candidates([1], '. .'), ['#  ', '  #'])
chk(candidates([2], '....'), ['##  ', ' ## ', '  ##'])
chk(candidates([2,1], '....'), ['## #'])

chk(candidates([1, 3, 1, 3, 10, 2], '# ### # .##....#....##...'), ['# ### # ### ########## ##'])

# reduce the search space for (clue, puzzle) by removing known prefixes and suffixes, although
# the innermost ' ' or '#' must be retained to maintain the boundary conditions for the solver.
# This function saved about 70% of compute time since candidates function is >n! in clue length
# and parts are linear in puzzle length.
def truncate(clue, puzzle):
	prefix = ''
	suffix = ''
	# remove runs of solved '#' and ' ' from the outside of puzzle
	# and return the simplified clue and puzzle and removed prefix/suffix
	while len(puzzle) > 2 and puzzle[0] != '.' and puzzle[1] != '.':
		if puzzle[0] == '#':
			assert clue[0] > 0
			clue[0] -= 1
			if clue[0] == 0:
				assert puzzle[1] == ' '
				clue = clue[1:]
		prefix = prefix + puzzle[0]
		puzzle = puzzle[1:]
	while len(puzzle) > 2 and puzzle[-1] != '.' and puzzle[-2] != '.':
		if puzzle[-1] == '#':
			assert clue[-1] > 0
			clue [-1] -= 1
			if clue[-1] == 0:
				assert puzzle[-2] == ' '
				clue = clue[:-1]
		suffix = puzzle[-1] + suffix
		puzzle = puzzle[:-1]
	print prefix, clue, puzzle, suffix
	return prefix, clue, puzzle, suffix

assert truncate([1, 3, 1, 3, 10, 2],   '# ### # .##....#....##...') == ('# ### #', [3,10,2], ' .##....#....##...', '')
assert truncate([1, 3, 1, 3, 10, 2],   '# ### # .##....#....## ##') == ('# ### #', [3,9], ' .##....#....#', '# ##')
assert truncate([1, 1, 2, 2, 2, 6, 1], '#     # #.............#..') == ('#     # ', [2, 2, 2, 6, 1], '#.............#..', '')
assert truncate([2, 1, 1, 1, 2, 5],    '  ##  # # #   .  ## #####') == ('  ##  # # #  ', [], ' . ', ' ## #####')
assert truncate([7, 2, 1, 2, 5],       '####### ........#. .#..#.') == ('#######', [2, 1, 2, 5], ' ........#. .#..#.', '')

p = Puzzle()
p.read('input.txt')

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

def free_spaces(clue, puzzle):
	return len(puzzle) - sum(clue) - (len(clue)-1)

unsolved = []
for n,x in enumerate(p.rows):
	unsolved.append( (free_spaces(x, '.'*25), 'r', n, x, getRowPuzzle, putRowPuzzle) )
for n,y in enumerate(p.cols):
	unsolved.append( (free_spaces(y, '.'*25), 'c', n, y, getColPuzzle, putColPuzzle) )
unsolved.sort()

print 'Starting'
h = 0
while unsolved:
	fs, rc, n, clue, statefn, updatefn = unsolved.pop(0)
	h += 1
	state = statefn(p, n)
	if not '.' in state: continue
	print 'Clue %60s state %s' % (str(clue), state)

	prefix, clue_mid, puzzle_mid, suffix = truncate(list(clue), state)

	state_next = list(puzzle_mid)
	char_sets = [set() for c in puzzle_mid]
	for c in candidates(clue_mid, puzzle_mid):
		# track the possible values for each position in state
		[x.add(y) for x,y in zip(char_sets, c)]
	infers = 0
	for i, (cs, s) in enumerate(zip(char_sets, puzzle_mid)):
		if len(cs) == 1:
			c = cs.pop()
			if s == '.':
				state_next[i] = c
				infers += 1
	s = prefix + ''.join(state_next) + suffix
	if s != state:
		updatefn(p, n, s)
		print ' Did partial solve in %d positions for %s %d - puzzle now' % (infers, rc, n)
		print '   from clue ' + str(clue) + ' state ' + state + " -> " + s
		print(p)
		h = 0
	if any(char_sets):
		unsolved.append( (fs, rc, n, clue, statefn, updatefn) )

	if h > 52:
		raise Exception('No iterative progress')

print '\n *** Solved ***'
print(p)
