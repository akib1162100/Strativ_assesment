import heapq
import random


class TemperaturePriorityQueue:
    def __init__(self, max_length=10):
        self.max_length = max_length
        self.heap = []

    def add_district(self, district_name, temperature):
        heapq.heappush(self.heap, (temperature, district_name))
        if len(self.heap) > self.max_length:
            heapq.heappop(self.heap)

    def get_priority_districts(self):
        return [district for _, district in sorted(self.heap)]
