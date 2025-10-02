import json
import random
from collections import defaultdict


class Predictor:
    def __init__(self, state_file, history_limit=50):
        self.state_file = state_file
        self.history_limit = history_limit
        self.load_state()

    def load_state(self):
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.markov = {
                    k: defaultdict(int, v) for k, v in data.get("markov", {}).items()
                }
        except:
            self.history = []
            self.markov = {}

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump({"history": self.history, "markov": self.markov}, f)

    def add_result(self, num):
        """Add new result and update Markov transitions"""
        self.history.append(num)
        if len(self.history) > self.history_limit:
            self.history.pop(0)

        if len(self.history) >= 2:
            a, b = self.history[-2], self.history[-1]
            if str(a) not in self.markov:
                self.markov[str(a)] = defaultdict(int)
            self.markov[str(a)][str(b)] += 1

        self.save_state()

    def predict_next(self):
        """Predict next number using Markov + Frequency + Recency"""
        if not self.history:
            return {"next": None, "color": None, "confidence": 0}

        last = str(self.history[-1])

        # 1. Markov Chain
        markov_pred = None
        if last in self.markov and self.markov[last]:
            markov_pred = int(max(self.markov[last], key=self.markov[last].get))

        # 2. Frequency
        freq_pred = max(set(self.history), key=self.history.count)

        # 3. Recency (last 5 trend)
        recency_pred = self.history[-5:]
        recency_pred = max(set(recency_pred), key=recency_pred.count)

        # Voting
        candidates = [markov_pred, freq_pred, recency_pred]
        candidates = [c for c in candidates if c is not None]

        if not candidates:
            final = random.randint(0, 9)
        else:
            final = max(set(candidates), key=candidates.count)

        confidence = round(candidates.count(final) / len(candidates), 2)
        color = "GREEN" if final % 2 else "RED"

        return {"next": final, "color": color, "confidence": confidence}
