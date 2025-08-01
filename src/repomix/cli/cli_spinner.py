import threading


class Spinner:
    def __init__(self, message: str):
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.message = message
        self.index = 0
        self.timer = None

    def spin(self):
        print(
            f"\r{self.spinner_chars[self.index % len(self.spinner_chars)]} {self.message}",
            end="",
        )
        self.index += 1
        self.timer = threading.Timer(0.1, self.spin)
        self.timer.start()

    def start(self):
        self.spin()

    def update(self, message: str):
        self.message = message

    def stop(self, final_message: str):
        if self.timer:
            self.timer.cancel()
        print(f"\r{final_message}\n", end="")

    def succeed(self, message: str):
        self.stop(f"✔ {message}")

    def fail(self, message: str):
        self.stop(f"✖ {message}")
