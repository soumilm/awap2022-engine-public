import heapq
from turtle import update


def dijkstra(map, row, col):
    dist = {}
    prev = {}

    HEIGHT = len(map)
    WIDTH = len(map[0])

    def getPassability(r, c):
        return map[r][c].passability

    def isValid(r, c):
        return 0 <= r and r < HEIGHT and 0 <= c and c < WIDTH

    def updateInPQ(pq, row, col, newCost):
        for i in range(len(pq)):
            (cost, (r, c)) = pq[i]
            if r == row and c == col:
                pq[i] = (newCost, (r, c))
                return True
        return False

    PQ = []

    for r in range(HEIGHT):
        for c in range(WIDTH):
            dist[(r, c)] = float("inf")
            prev[(r, c)] = None
            if r == row and c == col:
                heapq.heappush(PQ, (0.0, (r, c)))
                dist[(r, c)] = 0
            else:
                heapq.heappush(PQ, (float("inf"), (r, c)))

    while PQ:
        (r, c) = heapq.heappop(PQ)

        nbors = [(r, c + 1), (r, c - 1), (r + 1, c), (r - 1, c)]

        for (rn, cn) in nbors:
            alt = dist[(r, c)] + getPassability(r, c)
            if isValid(rn, cn) and alt < dist[(rn, cn)]:
                dist[(rn, cn)] = alt
                prev[(rn, rn)] = (r, c)
                updateInPQ(PQ, rn, cn, alt)

    return dist, prev
