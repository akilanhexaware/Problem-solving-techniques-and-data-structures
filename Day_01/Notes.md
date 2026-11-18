# Day 1 algorithm rationale

Run `python3 main.py` here. The program writes 50,000 deterministic synthetic orders to orders.csv and uses inline fixtures for bank and hospital scenarios. Times in output.txt measure matched lookup batches and independent sorts over the same data. Python's built-in sort is stable and can exploit ordered runs.

## Retail Order Desk

| Task | Rationale | Time | Extra space |
|---|---|---|---|
| Search | Linear requires no ordering. Binary halves the search interval using IDs already in ascending order. | O(n) vs O(log n) worst | O(1) |
| Sort | Insertion shifts larger sort keys one slot at a time. Merge splits the work and merges sorted halves. Both preserve input order for tied amounts. | O(n²) vs O(n log n) worst | O(n) copy, O(n) merge |
| Duplicates | Hash the customer ID, integer amount and timestamp minute. | O(n) expected | O(n) |
| Undo and dispatch | A list-backed stack retrieves the latest edit. A two-stack queue moves each order across once. Built-in list/deque have simpler interfaces and deque removes from the front directly. | O(1) amortized; deque end operations O(1) | O(n) |
| Refund | Greedy takes the largest usable denomination first. DP saves the optimum for each smaller amount and reconstructs the notes. | Greedy O(k log k + r); DP O(Ak + r) | O(k + r), O(A + r) |

Here A is the amount, k the number of denominations and r the number of notes in the returned result. For 6 with denominations 4, 3 and 1, greedy returns 4+1+1 and DP returns 3+3. The three descending insertion passes over [8, 2, 5, 3, 7] produce [8, 2, 5, 3, 7], [8, 5, 2, 3, 7] and [8, 5, 3, 2, 7]. The captured retail batch shows binary search faster because it probes a much smaller portion of the same records.

## Banking Transaction Review

| Operation | Best | Average | Worst | Extra space |
|---|---|---|---|---|
| Linear search | O(1) | O(n) | O(n) | O(1) |
| Binary search | O(1) | O(log n) | O(log n) | O(1) |
| Insertion sort | O(n) | O(n²) | O(n²) | O(n) copy |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Duplicate scan after sorting | O(n) | O(n) expected | O(n²) under pathological hash collisions | O(n) |
| Queue enqueue/dequeue | O(1) | O(1) amortized | O(n) refill | O(n) storage |
| Stack push/pop | O(1) | O(1) amortized | O(n) resize | O(n) storage |
| Divide-and-conquer min/max | O(n) | O(n) | O(n) | O(log n) |
| Brute-force min/max | O(n) | O(n) | O(n) | O(1) |

A probe counts one examined ID. The mean covers every successful target with equal weight. Stable sorts preserve the posting order for simultaneous credit A and credit B. Sorting by seconds before hashing adds O(n log n) worst-case time and supports an inclusive rolling 60-second test across minute boundaries. Divide-and-conquer shares a comparison for each two-element leaf before combining extremes, so it uses fewer comparisons than checking both bounds separately per row. A queue handles reviews in arrival order and the stack retrieves the latest adjustment first.

## Hospital Appointment Desk

Binary search visits at most about 15 records of a 20,000-row sorted roster per lookup. Linear search grows with roster size and the measured batch takes longer. The urgency sort uses descending urgency and ascending arrival. Selection makes O(n²) comparisons and at most n−1 swaps. Quicksort averages O(n log n) time and can take O(n²) on adverse partitions. Both copy the input. A quicksort exchange moves two distinct indices. A selection trace is printed in output.txt.

A set indexes patient/slot pairs in expected O(n) total time and O(n) space. Repeated list scans can take O(n²). A two-stack FIFO queue serves tokens in order and a LIFO stack retrieves the most recently viewed patient, both with amortized O(1) operations. Interval DP compares skipping a slot with attending it after the last compatible slot. Binary-search predecessors make sorting and DP O(n log n) with O(n) auxiliary space. Earliest finish gives the same optimal count for equally valued appointments by leaving maximal time for later slots. Touching endpoints are compatible.
