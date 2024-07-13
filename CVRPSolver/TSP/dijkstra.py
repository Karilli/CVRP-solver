from heapq import heapify, heappush, heappop
from math import inf


MIN_MEMO_SIZE = 8


class Memo:
    MEMO = []
    MASK_TO_NODES = []
    N = 0
    @classmethod
    def resize(cls, n):
        cls.N = max(MIN_MEMO_SIZE, n)
        cls.MEMO = [[inf] * (1 << cls.N) for _ in range(cls.N)]
        cls.MASK_TO_NODES = tuple(
            tuple(i for i in range(cls.N+1) if (1 << i) & mask)
            for mask in range(1 << (cls.N+1))
        )

    @classmethod
    def init(cls, n, route, dist):
        if cls.N < n:
            cls.resize(n)
            for x in range(n):
                cls.MEMO[x][1 << x] = dist[route[x]][0]
            return

        for x in range(n):
            for mask in range(1<<n):
                cls.MEMO[x][mask] = inf
            cls.MEMO[x][1 << x] = dist[route[x]][0]

    @classmethod
    def extract(cls, x, n, route, dist):
        res = [route[x]]
        v = (1 << n) - 1
        for _ in range(n-1):
            u = (~ (1 << x)) & v
            _, y = min((Memo.MEMO[y][u] + dist[route[x]][route[y]], y) for y in cls.MASK_TO_NODES[u])
            res.append(route[y])
            x, v = y, u
        return res


def dijkstra(route, dist):
    n = len(route)
    if n == 1:
        return 2*dist[route[0]][0], route

    heap = [(dist[route[x]][0], x, 1 << x) for x in range(n)]
    heapify(heap)
    Memo.init(n, route, dist)

    while heap:
        d, x, v = heappop(heap)
        if v == (1 << n) - 1:
            break
        for y in range(n):
            if x != y:
                u = (1 << y) | v
                new_distance = Memo.MEMO[x][v] + dist[route[x]][route[y]] + (u == (1 << n) - 1) * dist[route[y]][0]
                if new_distance < Memo.MEMO[y][u]:
                    Memo.MEMO[y][u] = new_distance
                    heappush(heap, (new_distance, y, u))

    return d, Memo.extract(x, n, route, dist)


def dp(route, dist):
    # NOTE: this was created by GPT, idk how it works, but it definitely works
    # TODO: precomputing it in Memo could be faster
    def generate_masks(m):
        """
        Generates a sequence of all unique numbers with a bit_length of m (with trailing zeroes)
        that contain at least two 1 bits, ensuring that each pair of consecutive numbers in the
        sequence has the first number with fewer or equal 1 bits compared to the following number.

        In other words, if S is the generated sequence of m, it holds that:
        ```
        N = len(S)
        for i in range(N):
            assert 2 <= S[i].bit_count() 
        
        for a1, a2 in zip(S, S[1:]):
            assert a1.bit_count() <= a2.bit_count()
        
        assert N == len(set(S))             # the numbers are unique
        assert N == 2**m - m - 1            # and there are all of them
        assert all(2 < a < 2**m for a in S) # ...
        ```

        >>> N = 4
        >>> [bin(n)[2:].ljust(N, "0") for n in generate_masks(N)]
        ['0011', '0101', '0110', '1001', '1010', '1100', '0111', '1011', '1101', '1110', '1111']
        """
        for n in range(2, m+1):
            max_num = 1 << m
            num = (1 << n) - 1
            while num < max_num:
                yield num
                c = num & -num
                r = num + c
                num = (((r ^ num) >> 2) // c) | r

    n = len(route)
    Memo.init(n, route, dist)

    for mask in generate_masks(n):
        for x in Memo.MASK_TO_NODES[mask]:
            for y in Memo.MASK_TO_NODES[mask & ~(1 << x)]:
                Memo.MEMO[x][mask] = min(Memo.MEMO[x][mask], Memo.MEMO[y][mask & ~(1 << x)] + dist[route[x]][route[y]])

    d, x = min((Memo.MEMO[x][(1 << n) - 1] + dist[route[x]][0], x) for x in range(n))
    return d, Memo.extract(x, n, route, dist)
