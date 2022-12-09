"""
Observe pattern objects for use in communicating between UI/backend

Loosely based on Godots' signal design pattern.
"""


from typing import List


class Event:
    pass

class Observable:

    def __init__(self, signals: List[str]):
        self.signals = signals
        self.callbacks = {s: [] for s in self.signals}

    def subscribe(self, signal: str, callback: function):
        self.callbacks[signal].append(callback)

    def emit_signal(self, signal: str, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.items():
            setattr(e, k, v)
        for fn in self.callbacks[signal]:
            fn(e)