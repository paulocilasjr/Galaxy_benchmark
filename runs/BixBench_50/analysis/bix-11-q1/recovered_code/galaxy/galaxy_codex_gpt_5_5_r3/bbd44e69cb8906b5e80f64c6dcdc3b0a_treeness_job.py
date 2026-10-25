import sys, zipfile, statistics, re, math

number_re = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?')

class Parser:
    def __init__(self, text):
        self.s = text.strip()
        self.n = len(self.s)
        self.total = 0.0
        self.internal = 0.0

    def skip_ws_comments(self, i):
        while i < self.n:
            if self.s[i].isspace():
                i += 1
                continue
            if self.s[i] == '[':
                depth = 1
                i += 1
                while i < self.n and depth:
                    if self.s[i] == '[':
                        depth += 1
                    elif self.s[i] == ']':
                        depth -= 1
                    i += 1
                continue
            break
        return i

    def parse_label(self, i):
        i = self.skip_ws_comments(i)
        if i < self.n and self.s[i] == "'":
            i += 1
            while i < self.n:
                if self.s[i] == "'":
                    if i + 1 < self.n and self.s[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            return self.skip_ws_comments(i)
        while i < self.n and self.s[i] not in ':,();':
            if self.s[i] == '[':
                break
            i += 1
        return self.skip_ws_comments(i)

    def parse_length(self, i):
        i = self.skip_ws_comments(i)
        if i >= self.n or self.s[i] != ':':
            return i, None
        i += 1
        i = self.skip_ws_comments(i)
        m = number_re.match(self.s, i)
        if not m:
            raise ValueError('branch length expected near offset %d' % i)
        value = float(m.group(0))
        i = m.end()
        return self.skip_ws_comments(i), value

    def parse_subtree(self, i):
        i = self.skip_ws_comments(i)
        if i >= self.n:
            raise ValueError('unexpected end of tree')
        if self.s[i] == '(':
            i += 1
            child_count = 0
            while True:
                i = self.parse_subtree(i)
                child_count += 1
                i = self.skip_ws_comments(i)
                if i < self.n and self.s[i] == ',':
                    i += 1
                    continue
                if i < self.n and self.s[i] == ')':
                    i += 1
                    break
                raise ValueError('expected comma or close parenthesis near offset %d' % i)
            if child_count == 0:
                raise ValueError('internal node without children')
            i = self.parse_label(i)
            i, length = self.parse_length(i)
            if length is not None:
                self.total += length
                self.internal += length
            return i
        else:
            i = self.parse_label(i)
            i, length = self.parse_length(i)
            if length is not None:
                self.total += length
            return i

    def treeness(self):
        i = self.parse_subtree(0)
        i = self.skip_ws_comments(i)
        if i < self.n and self.s[i] == ';':
            i += 1
        i = self.skip_ws_comments(i)
        if i != self.n:
            raise ValueError('unexpected trailing text near offset %d' % i)
        if self.total <= 0.0:
            raise ValueError('non-positive total branch length')
        return self.internal / self.total

def compute_group(zip_path):
    rows = []
    failures = []
    with zipfile.ZipFile(zip_path) as zf:
        names = sorted(n for n in zf.namelist() if n.endswith('.treefile') and not n.endswith('/'))
        for name in names:
            try:
                raw = zf.read(name).decode('utf-8').strip()
                if not raw:
                    raise ValueError('empty treefile')
                val = Parser(raw).treeness()
                if not math.isfinite(val):
                    raise ValueError('non-finite treeness')
                rows.append((name, val))
            except Exception as exc:
                failures.append((name, str(exc)))
    if not rows:
        raise RuntimeError('no valid .treefile members in %s' % zip_path)
    return names, rows, failures

def fmt(x):
    return format(x, '.17g')

animals_zip, fungi_zip, summary_path, answer_path = sys.argv[1:5]
results = {}
for group, path in [('animals', animals_zip), ('fungi', fungi_zip)]:
    names, rows, failures = compute_group(path)
    median = statistics.median(v for _, v in rows)
    results[group] = {'names': names, 'rows': rows, 'failures': failures, 'median': median}

diff = results['fungi']['median'] - results['animals']['median']
with open(summary_path, 'w', encoding='utf-8') as out:
    out.write('record\tgroup\tmember\ttreeness\tn_treefiles\tn_valid\tn_failed\tmedian_treeness\tdifference_fungi_minus_animals\n')
    for group in ['animals', 'fungi']:
        r = results[group]
        for member, value in r['rows']:
            out.write('tree\t%s\t%s\t%s\t%d\t%d\t%d\t%s\t\n' % (group, member, fmt(value), len(r['names']), len(r['rows']), len(r['failures']), fmt(r['median'])))
    out.write('difference\tfungi_minus_animals\t\t\t%d\t%d\t%d\t\t%s\n' % (len(results['animals']['names']) + len(results['fungi']['names']), len(results['animals']['rows']) + len(results['fungi']['rows']), len(results['animals']['failures']) + len(results['fungi']['failures']), fmt(diff)))
with open(answer_path, 'w', encoding='utf-8') as out:
    out.write(fmt(diff) + '\n')
