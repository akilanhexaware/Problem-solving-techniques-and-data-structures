import csv
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from random import Random
from time import perf_counter

ROOT = Path(__file__).resolve().parent


def linear(rows, target):
    for i, row in enumerate(rows, 1):
        if row[0] == target:
            return row, i
    return None, len(rows)


def binary(rows, target):
    low, high, probes = 0, len(rows) - 1, 0
    while low <= high:
        middle = (low + high) // 2
        probes += 1
        key = rows[middle][0]
        if key == target:
            return rows[middle], probes
        if key < target:
            low = middle + 1
        else:
            high = middle - 1
    return None, probes


def insertion(rows, key):
    result = list(rows)
    for i in range(1, len(result)):
        row = result[i]
        j = i
        while j and key(result[j - 1]) > key(row):
            result[j] = result[j - 1]
            j -= 1
        result[j] = row
    return result


def merge_sort(rows, key):
    if len(rows) < 2:
        return list(rows)
    mid = len(rows) // 2
    a, b = merge_sort(rows[:mid], key), merge_sort(rows[mid:], key)
    merged = []
    i = j = 0
    while i < len(a) and j < len(b):
        if key(a[i]) <= key(b[j]):
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    return merged + a[i:] + b[j:]


def selection(rows, key, trace=False):
    out, swaps = list(rows), 0
    for i in range(len(out) - 1):
        smallest = min(range(i, len(out)), key=lambda j: key(out[j]))
        if i != smallest:
            out[i], out[smallest] = out[smallest], out[i]
            swaps += 1
        if trace and i < 3:
            print('Selection pass', i + 1, out)
    return out, swaps


def quick_sort(rows, key):
    out, swaps = list(rows), 0
    pending = [(0, len(out) - 1)]
    while pending:
        lo, hi = pending.pop()
        if lo >= hi:
            continue
        pivot = key(out[(lo + hi) // 2])
        i, j = lo, hi
        while i <= j:
            while key(out[i]) < pivot:
                i += 1
            while key(out[j]) > pivot:
                j -= 1
            if i <= j:
                if i < j:
                    out[i], out[j] = out[j], out[i]
                    swaps += 1
                i += 1
                j -= 1
        pending.extend(((lo, j), (i, hi)))
    return out, swaps


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()


class Queue:
    def __init__(self):
        self.incoming, self.outgoing = Stack(), Stack()

    def enqueue(self, item):
        self.incoming.push(item)

    def dequeue(self):
        if not self.outgoing.items:
            while self.incoming.items:
                self.outgoing.push(self.incoming.pop())
        return self.outgoing.pop()


def workflows(first, second):
    queue, stack = Queue(), Stack()
    for item in (first, second):
        queue.enqueue(item)
        stack.push(item)
    assert (queue.dequeue(), queue.dequeue(), stack.pop()) == (first, second, second)
    builtin_queue, builtin_stack = deque((first, second)), [first, second]
    assert (builtin_queue.popleft(), builtin_queue.popleft(), builtin_stack.pop()) == (first, second, second)
    print('FIFO:', first, second, '| LIFO:', second)


def duplicates(rows, key):
    seen, repeated = set(), []
    for row in rows:
        k = key(row)
        if k in seen:
            repeated.append(row)
        seen.add(k)
    return repeated


def greedy(amount, coins):
    result = []
    for coin in sorted(coins, reverse=True):
        count, amount = divmod(amount, coin)
        result.extend([coin] * count)
    return result if amount == 0 else None


def optimal(amount, coins):
    best = [0] + [float('inf')] * amount
    chosen = [0] * (amount + 1)
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value], chosen[value] = best[value - coin] + 1, coin
    if not chosen[amount] and amount:
        return None
    out = []
    while amount:
        coin = chosen[amount]
        out.append(coin)
        amount -= coin
    return out


def timed(label, fn):
    start = perf_counter()
    result = fn()
    print(f'{label}: {perf_counter() - start:.6f} s')
    return result


def retail():
    rng = Random(11)
    start = datetime(2026, 10, 14, 9)
    with (ROOT / 'orders.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('orderId', 'customerId', 'amount', 'createdAt'))
        for i in range(50000):
            customer, amount, offset = (1, 100, 0) if i < 2 else (rng.randrange(1000), rng.randrange(1, 50000), i)
            writer.writerow((i + 1, customer, amount, (start + timedelta(seconds=offset)).isoformat()))
    with (ROOT / 'orders.csv').open(newline='') as f:
        orders = [(int(a), int(b), int(c), d) for a, b, c, d in list(csv.reader(f))[1:]]
    targets = [rng.randrange(1, 50002) for _ in range(200)]
    results = [timed(fn.__name__, lambda: [fn(orders, t)[0] for t in targets]) for fn in (linear, binary)]
    assert results[0] == results[1] and binary(orders, 50001)[0] is None
    key = lambda row: -row[2]
    sample = orders[:10000]
    expected = timed('Built-in sort', lambda: sorted(sample, key=key))
    assert timed('Insertion sort', lambda: insertion(sample, key)) == expected
    assert timed('Merge sort', lambda: merge_sort(sample, key)) == expected
    amounts = [8, 2, 5, 3, 7]
    for i in range(1, 4):
        print(f'Insertion pass {i}:', insertion(amounts[:i+1], lambda n: -n) + amounts[i+1:])
    repeated = duplicates(orders, lambda r: (r[1], r[2], r[3][:16]))
    assert repeated[0][0] == 2
    print('Duplicate count:', len(repeated), '| first:', repeated[0])
    workflows('order #1 original edit', 'order #2 latest edit')
    print('Refund 68:', greedy(68, (50, 20, 10, 5, 2, 1)))
    assert greedy(6, (4, 3, 1)) == [4, 1, 1] and optimal(6, (4, 3, 1)) == [3, 3]
    print('Refund 6, greedy:', greedy(6, (4, 3, 1)), 'DP:', optimal(6, (4, 3, 1)))


def extrema(values, lo, hi):
    if hi - lo == 1:
        return values[lo], values[lo], 0
    if hi - lo == 2:
        a, b = values[lo:hi]
        return (a, b, 1) if a <= b else (b, a, 1)
    mid = (lo + hi) // 2
    a, b, x = extrema(values, lo, mid)
    c, d, y = extrema(values, mid, hi)
    return min(a, c), max(b, d), x + y + 2


def banking():
    rows = [(i,) for i in range(1, 100001)]
    probes = [0] * (len(rows) + 1)
    pending = [(0, len(rows) - 1, 1)]
    while pending:
        lo, hi, depth = pending.pop()
        if lo <= hi:
            mid = (lo + hi) // 2
            probes[mid + 1] = depth
            pending.extend(((lo, mid - 1, depth + 1), (mid + 1, hi, depth + 1)))
    assert all(binary(rows, i)[1] == probes[i] for i in range(1, len(rows)+1))
    print('Best/mean/worst successful key probes:', (min(probes[1:]), sum(probes)/len(rows), max(probes)), 'linear:', (1, 50000.5, 100000))
    postings = [(2, 'credit A'), (1, 'debit'), (2, 'credit B')]
    assert insertion(postings, lambda x: x[0]) == merge_sort(postings, lambda x: x[0]) == [postings[1], postings[0], postings[2]]
    print('Stable statement:', insertion(postings, lambda x: x[0]))
    samples = [('acct1', 500, 'Shop', t) for t in (0, 60, 121)] + [('acct2', 500, 'Shop', 122)]
    latest, repeated = {}, []
    for account, amount, merchant, seconds in sorted(samples, key=lambda row: row[3]):
        key = account, amount, merchant
        if key in latest and seconds - latest[key] <= 60:
            repeated.append(seconds)
        latest[key] = seconds
    assert repeated == [60]
    print('Rolling 60-second duplicates:', repeated)
    workflows('adjustment A', 'adjustment B')
    values = [31, 2, 120, 15, -4, 80, 13, 25]
    lo, hi, comparisons = extrema(values, 0, len(values))
    brute_lo = brute_hi = values[0]
    for value in values[1:]:
        if value < brute_lo:
            brute_lo = value
        if value > brute_hi:
            brute_hi = value
    assert (lo, hi) == (brute_lo, brute_hi)
    print('Day min/max:', lo, hi, '| divide-and-conquer:', comparisons, '| scan:', 2*(len(values)-1))


def hospital():
    rng = Random(22)
    rows = [(i, f'Patient {i}') for i in range(20000)]
    targets = [rng.randrange(20000) for _ in range(1000)]
    results = [timed(fn.__name__, lambda: [fn(rows, t)[0] for t in targets]) for fn in (linear, binary)]
    assert results[0] == results[1]
    slots = [(rng.randrange(1, 6), i) for i in range(500)]
    key = lambda row: (-row[0], row[1])
    a, sa = timed('Selection', lambda: selection(slots, key))
    b, sb = timed('Quicksort', lambda: quick_sort(slots, key))
    assert a == b == sorted(slots, key=key)
    print('Swaps:', sa, sb)
    selection(slots[:5], key, trace=True)
    bookings = [('P1', '09:00'), ('P2', '09:00'), ('P1', '09:00')]
    assert duplicates(bookings, lambda row: row) == [bookings[-1]]
    print('Double bookings:', duplicates(bookings, lambda row: row))
    workflows('token 101', 'token 102')
    intervals = sorted([(0, 9), (0, 2), (2, 5), (5, 8), (6, 10)], key=lambda x: x[1])
    from bisect import bisect_right
    ends = [end for _, end in intervals]
    best = [0]
    for i, (start, _) in enumerate(intervals):
        best.append(max(best[-1], 1 + best[bisect_right(ends, start, hi=i)]))
    greedy_count, end = 0, -1
    for start, finish in intervals:
        if start >= end:
            greedy_count, end = greedy_count + 1, finish
    assert best[-1] == greedy_count == 3
    print('Slots:', intervals, '| DP/earliest-finish:', best[-1], greedy_count)


if __name__ == '__main__':
    for label, run in [('Retail', retail), ('Banking', banking), ('Hospital', hospital)]:
        print(f'\n{label}')
        run()
        print('PASS')
