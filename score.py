import itertools

def read(fn = 'human.txt'):
	with open('human.txt') as f:
		cs = []
		puzz, rows = [], []
		for n,l in enumerate(f.readlines()):
			if n < 9:
				cs.append(l[20:45])
			if n > 8:
				r = map(int, l[0:20].strip().split(' '))
				p = l[20:45]
				#  '.'' unknown   ' ' known blank, '#' known filled
				print "%50s >%25s<" % (str(r), p)
				assert all([x in ' .#' for x in p])
				puzz.append(p)
				rows.append(r)
		cols = [ [int(x) for x in y if x != ' '] for y in zip(*cs)]
		print 'rows: %s' % rows
		print 'cols: %s' % cols
	return rows, cols, puzz

# generate candidate solutions for puzzle given clue
def candidates_perm(clue, puzzle):
	# every dot in puzzle can be 0 or 1, but only some of these will
	# agree with the groupings in clue, and have the right number of
	# filled squares
	sq = sum(clue)
	dots,hashes = puzzle.count('.'), puzzle.count('#')
	hashes_to_find = sum(clue) - puzzle.count('#')
	missing_parts = (' '*(dots - hashes_to_find)) + ('#'*hashes_to_find)
	print("missing parts '%s' in puzzle '%s'" % (missing_parts, puzzle))

	assert(len(missing_parts) == dots)
	ps = []
	seen = set()

	for x in itertools.permutations(missing_parts):
		if x in seen:
			continue
		# interlace back into puzzle
		seen.add(x)
		xs = list(x)
		c = list()
		print "puzzle '%s' xs %s" % (puzzle, x)
		for p in puzzle:
			if p == ' ' or p == '#':
				c.append(p)
			else:
				c.append(xs.pop())
		# does cand match the clue? Are there the right number of like subsequences
		# with minimum one space between?
		cand = ''.join(c)
		clue_for_cand = [len(list(g)) for k, g in itertools.groupby(cand) if k == '#']
		print "   cand '%s' clue_for_cand %s" % (cand, clue_for_cand)
		if clue_for_cand == clue:
			ps.append(cand)
	print ps
	return ps

def chk(got, expected):
	if not expected == got:
		print("Failed, \n  expected: %s\n  got:      %s" % (expected, got))
		raise Exception("failed")

candidates = candidates_perm
chk(candidates([3], '...'), ['###'])
chk(candidates([3], '.#.'), ['###'])
chk(candidates([2], '.#.'), ['## ', ' ##'])
chk(candidates([2], '...'), ['## ', ' ##'])
chk(candidates([1, 1], '...'), ['# #'])
chk(candidates([1], '. .'), ['#  ', '  #'])
chk(candidates([2], '....'), ['##  ', ' ## ', '  ##'])
chk(candidates([2,1], '....'), ['## #'])

# hmm, 110 seconds. not going anywhere with candidates_perm
chk(candidates([1, 3, 1, 3, 10, 2], '# ### # .##....#....##...'), ['# ### # ### ########## ##'])

# p = read()

