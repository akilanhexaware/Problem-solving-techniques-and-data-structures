# Day 2 algorithm choices

Run `python3 main.py`. All fixtures, including the ten-hub adjacency list, are in the program. output.txt records all three sets. In the table, h is BST height, V and E are graph vertices and edges, and n is the input length. Auxiliary space excludes returned results unless stated.

| Set and task | Pattern and reason | Time | Auxiliary space |
|---|---|---|---|
| Catalogue categories | BST allows ordered traversal with insert and search. Inorder lists categories alphabetically. | O(h) per insert/search; O(nh) traversal upper bound for this list-building implementation | O(1) insert/search, O(n+h) traversal |
| SKU lookup | Chaining retains full keys in each bucket. Keys 3 and 8 collide modulo 5. A dict provides the same lookup interface with lower overhead in this run. | O(1) expected with bounded load; O(n) worst lookup | O(n+b) for b buckets |
| Deploy dependencies | Postorder DFS visits prerequisites first. A node on the active path identifies a cycle. | O(V+E) | O(V) |
| Peak catalogue traffic | Add the incoming minute and subtract the outgoing one. Report the earliest maximum. | O(n) | O(k) initial width-k slice |
| Gift cards | Low/high pointers exploit sorted values. Emit distinct value pairs, including an equal pair if it occurs twice. | O(n) | O(1) |
| Claim IDs | BST inorder returns sorted IDs. A repeated ID leaves the tree unchanged. | O(h) per operation; O(nh) traversal upper bound | O(n+h) for traversal |
| Claim duplicates | Case-fold and remove whitespace, then use the policy/date tuple as the key. Python uses equality to resolve hash collisions. | O(n) expected for bounded-length pairs | O(n) |
| Approval stages | BFS finds the fewest transitions. DFS active state detects directed loops. | O(V+E) | O(V) |
| Claim spikes | Reset the window start after each day at or below 100. | O(n) | O(1) |
| Regional claims | Merge with two pointers; preserve duplicates and the order within each office. | O(n+m) | O(n+m) including output |
| Hub lookup | BST edge height is 3 for the fixture and 9 for sorted insertion. Sorted insertion makes a linear chain. | O(h) insert/search; O(n) height | O(n) worst height scan |
| Parcel scans | Dict maps each parcel to its scan trail. A set tracks repeated parcel/hub tuples. | O(n) expected | O(n) |
| Hub routes | BFS reconstructs the shortest unweighted route. DFS finds the reachable component. | O(V+E) | O(V+E) upper bound for the DFS stack |
| Peak parcel window | Maximizing the total maximizes the average for a fixed four-hour width. | O(n) | O(1) at fixed width |
| Route palindrome | Extract case-folded hub tokens and compare opposing codes. | O(n) | O(n) for normalized tokens |

The insurance tests cover empty inputs, repeated claim IDs, case/space variants, zero-length streaks, unreachable stages, loops and duplicate values in the merge.
