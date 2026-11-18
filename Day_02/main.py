from collections import deque
from random import Random
from re import findall
from time import perf_counter


class BST:
    def __init__(self, value):
        self.value, self.left, self.right = value, None, None

    def insert(self, value):
        node = self
        while value != node.value:
            side = 'left' if value < node.value else 'right'
            child = getattr(node, side)
            if child is None:
                setattr(node, side, BST(value))
                return
            node = child

    def search(self, value):
        node = self
        while node and value != node.value:
            node = node.left if value < node.value else node.right
        return node is not None

    def walk(self, order):
        left = self.left.walk(order) if self.left else []
        right = self.right.walk(order) if self.right else []
        root = [self.value]
        if order == 'inorder':
            return left + root + right
        if order == 'preorder':
            return root + left + right
        return left + right + root

    def height(self):
        pending, height = [(self, 0)], 0
        while pending:
            node, depth = pending.pop()
            height = max(height, depth)
            pending.extend((child, depth + 1) for child in (node.left, node.right) if child)
        return height


def tree(values):
    if not values:
        return None
    root = BST(values[0])
    for value in values[1:]:
        root.insert(value)
    return root


class ChainedMap:
    def __init__(self, size):
        self.buckets = [[] for _ in range(size)]

    def bucket(self, key):
        return self.buckets[key % len(self.buckets)]

    def put(self, key, value):
        bucket = self.bucket(key)
        for index, (stored, _) in enumerate(bucket):
            if stored == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key):
        return next((value for stored, value in self.bucket(key) if stored == key), None)


def dependency_order(graph):
    state, order = {}, []

    def visit(node):
        if state.get(node) == 1:
            raise ValueError(f'Circular dependency at {node}')
        if state.get(node) == 2:
            return
        state[node] = 1
        for dependency in graph.get(node, ()):
            visit(dependency)
        state[node] = 2
        order.append(node)

    for node in graph:
        visit(node)
    return order


def shortest(graph, origin, destination):
    queue, parent = deque([origin]), {origin: None}
    while queue:
        node = queue.popleft()
        if node == destination:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]
        for neighbor in graph.get(node, ()):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    return []


def reachable(graph, origin):
    seen, pending = set(), [origin]
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(graph.get(node, ()))
    return seen


def window(values, width):
    if not 0 < width <= len(values):
        return None
    total = best = sum(values[:width])
    start = 0
    for i in range(width, len(values)):
        total += values[i] - values[i-width]
        if total > best:
            start, best = i-width+1, total
    return start, best


def gift_pairs(values, target):
    result, lo, hi = [], 0, len(values)-1
    while lo < hi:
        a, b = values[lo], values[hi]
        if a+b < target:
            lo += 1
        elif a+b > target:
            hi -= 1
        else:
            result.append((a, b))
            while lo < hi and values[lo] == a:
                lo += 1
            while lo < hi and values[hi] == b:
                hi -= 1
    return result


def print_walks(root, values):
    assert root.walk('inorder') == sorted(set(values))
    for order in ('inorder', 'preorder', 'postorder'):
        print(order, root.walk(order))


def catalogue():
    categories = 'Home Clothes Sports Books Electronics Kitchen Toys Audio Cameras Denim Games Lights Shoes Tech Travel'.split()
    root = tree(categories)
    assert root.search('Tech') and not root.search('Cars')
    print_walks(root, categories)
    collision = ChainedMap(5)
    collision.put(3, 'SKU 3')
    collision.put(8, 'SKU 8')
    assert collision.get(3) == 'SKU 3' and collision.get(8) == 'SKU 8'
    print('Collision bucket:', collision.bucket(3))
    table, builtin = ChainedMap(65536), {}
    for sku in range(100000):
        table.put(sku, sku * 2)
        builtin[sku] = sku * 2
    targets = Random(13).sample(range(100000), 100000)
    results = []
    for name, lookup in [('Chained map', table.get), ('dict', builtin.get)]:
        tick = perf_counter()
        results.append([lookup(sku) for sku in targets])
        print(f'{name}, 100000 lookups: {perf_counter()-tick:.6f} s')
    assert results[0] == results[1]
    graph = {'cart': ['pricing'], 'pricing': ['inventory'], 'orders': ['cart', 'inventory'], 'inventory': []}
    order = dependency_order(graph)
    assert all(order.index(d) < order.index(s) for s in graph for d in graph[s])
    print('Deployment:', order)
    try:
        dependency_order({**graph, 'inventory': ['cart']})
    except ValueError as error:
        print(error)
    else:
        raise AssertionError('Cycle was missed')
    rng = Random(4)
    traffic = [rng.randrange(80, 100) for _ in range(1440)]
    traffic[600:780] = [150] * 180
    assert window(traffic, 180) == (600, 27000)
    print('Peak 3-hour window:', window(traffic, 180))
    pairs = gift_pairs([1, 1, 3, 5, 5, 7, 9], 10)
    assert pairs == [(1, 9), (3, 7), (5, 5)]
    print('Pairs:', pairs)


def repeated_keys(records, key):
    seen, duplicates = set(), []
    for item in records:
        normalized = key(item)
        if normalized in seen:
            duplicates.append(item)
        seen.add(normalized)
    return duplicates


def claim_duplicates(claims):
    return repeated_keys(claims, lambda row: tuple(''.join(value.split()).casefold() for value in row))


def streak(values):
    start = best = 0
    for i, value in enumerate(values):
        if value <= 100:
            start = i + 1
        best = max(best, i - start + 1)
    return best


def merge_claims(a, b):
    i = j = 0
    result = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    return result + a[i:] + b[j:]


def insurance():
    ids = [30, 10, 45, 20, 35, 30]
    root = tree(ids)
    assert root.search(35) and not root.search(1) and tree([]) is None
    print_walks(root, ids)
    claims = [('POL 1', '2026-10-14'), ('pol1', '2026-10-14'), ('POL 1', '2026-10-15')]
    assert claim_duplicates([]) == [] and claim_duplicates(claims) == [claims[1]]
    print('Duplicate claims:', claim_duplicates(claims))
    graph = {'Registration': ['Assessment'], 'Assessment': ['Surveyor', 'Settlement'], 'Surveyor': ['Settlement'], 'Settlement': []}
    path = shortest(graph, 'Registration', 'Settlement')
    assert path == ['Registration', 'Assessment', 'Settlement'] and not shortest(graph, 'Settlement', 'Registration')
    print('Shortest path:', path)
    print('Acyclic workflow:', dependency_order(graph)[::-1])
    try:
        dependency_order({**graph, 'Settlement': ['Assessment']})
    except ValueError as error:
        print(error)
    else:
        raise AssertionError('Loop was missed')
    assert streak([]) == 0 and streak([100, 101, 140, 121, 99, 110]) == 3
    assert merge_claims([], []) == [] and merge_claims([10, 25], [10, 30]) == [10, 10, 25, 30]
    print('Longest >100 run:', streak([100, 101, 140, 121, 99, 110]))
    print('Merged claims:', merge_claims([10, 25], [10, 30]))


def palindrome(text):
    codes = findall(r'[a-z0-9]+', text.casefold())
    left, right = 0, len(codes)-1
    while left < right:
        if codes[left] != codes[right]:
            return False
        left += 1
        right -= 1
    return True


def logistics():
    codes = 'DEL BOM HYD BLR CHE GOI JAI CCU AMD PUN'.split()
    root = tree(codes)
    assert root.search('PUN') and not root.search('LKO')
    print('Insertion order / sorted edge height:', root.height(), tree(sorted(codes)).height())
    scans = [('P01', 'DEL'), ('P02', 'BOM'), ('P01', 'BOM'), ('P01', 'DEL')]
    lookup = {p: [] for p, _ in scans}
    for parcel, hub in scans:
        lookup[parcel].append(hub)
    duplicates = repeated_keys(scans, lambda row: row)
    assert duplicates == [('P01', 'DEL')]
    print('Tracking:', lookup['P01'], '| repeat:', duplicates)
    links = [('DEL','JAI'), ('DEL','CCU'), ('DEL','HYD'), ('JAI','AMD'), ('AMD','BOM'),
             ('BOM','PUN'), ('BOM','GOI'), ('GOI','BLR'), ('HYD','BLR'), ('BLR','CHE')]
    graph = {code: [] for code in codes}
    for a, b in links:
        graph[a].append(b)
        graph[b].append(a)
    print('Adjacency:', graph)
    path = shortest(graph, 'DEL', 'CHE')
    assert path == ['DEL', 'HYD', 'BLR', 'CHE'] and reachable(graph, 'DEL') == set(codes)
    print('BFS route:', path, '| DFS reachable:', sorted(reachable(graph, 'DEL')))
    start, total = window([2, 7, 12, 16, 15, 13, 3, 1], 4)
    assert (start, total) == (2, 56)
    print('Peak 4-hour window:', start, total/4)
    assert palindrome('DEL / bom - del') and not palindrome('DEL / BOM / CHE')
    print('DEL / bom - del is a palindrome')


if __name__ == '__main__':
    for label, run in [('Catalogue', catalogue), ('Insurance', insurance), ('Logistics', logistics)]:
        print(f'\n{label}')
        run()
        print('PASS')
