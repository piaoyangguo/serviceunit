def find_de_prev(query, limit=0):
	chars = ['的', '得', '地']
	l = len(query)-1
	found = -1
	cnt = 0
	for i in range(len(query)-1, -1, -1):
		if limit > 0:
			if found < 0 and cnt == limit:
				break
		if query[i] in chars:
			found = i
		elif found >= 0:
			break
		cnt += 1
	if found < 0:
		return query
	return query[:found]

def find_split_next(query, limit=0):
	sptrim = [' ', ',', '，']
	spchars = sptrim + ['!', ';', '。', '！', '；']
	l = len(query)-1
	found = -1
	cnt = 0
	for i in range(0, len(query)):
		if limit > 0:
			if found < 0 and cnt == limit:
				break
		if query[i] in spchars:
			found = i
		elif found >= 0:
			break
		cnt += 1
	query =  query[found+1:]
	if query[:2] in ['让他', '请他', '叫他'] and query[2] not in ['们', '的']:
		query = query[2:]
	return query

def find_split_prev(query, limit=0):
	sptrim = [' ', ',', '，']
	spchars = sptrim + ['!', ';', '。', '！', '；']
	l = len(query)-1
	found = -1
	cnt = 0
	for i in range(len(query)-1, -1, -1):
		if limit > 0:
			if found < 0 and cnt == limit:
				break
		if query[i] in spchars:
			found = i
		elif found >= 0:
			break
		cnt += 1
	if found < 0:
		return query
	if query[found] in sptrim:
		return query[:found]
	return query[:found+1]
