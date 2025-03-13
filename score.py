
from datetime import datetime as dt
import time
import random


class GameManager():
    def __init__(self):
        self.score = 0
        self.timer = 0
        self.total_count = 0
        self.message = None
        self.correct = None

    def updater(self, timer):
        while self.timer != timer:
            value = self.count_down(1)
            self.timer += 1
            if value < 10:
                return f"00:0{value}"
            else:
                return f"00:{value}"



    def count_down(self, timer):
        self.timer += 1
        time.sleep(timer)
        return self.timer


    def score_manager(self, is_correct):
        if is_correct:
            self.score += 1
            self.total_count += 1
        else:
            self.total_count += 1




