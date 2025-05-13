import threading
from rocket import Rocket


class ControlCenter:
    def __init__(self):
        self.rockets_data_store: dict[str, Rocket] = {}
        self.store_lock = threading.Lock()

    def process_incoming_message(message: any):
        print(message)