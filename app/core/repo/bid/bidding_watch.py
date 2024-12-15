import time
import asyncio
# class Stopwatch:
#     """
#     This class is used to time each bid that goes on the stack.
#     The time between each bid determines when the auction closes.
#     """
#     def __init__(self):
#         self.total_time = 0.0  # Attribute to store the total time in seconds
#         self._start_time = None  # Internal attribute to store the start time
#         self._running = False  # Internal flag to check if the stopwatch is running
#
#     def start(self):
#         """Starts the stopwatch if it is not already running."""
#         if not self._running:
#             self._start_time = time.time()  # Record the current time as the start time
#             self._running = True
#             print("Stopwatch started.")
#         else:
#             print("Stopwatch is already running.")
#
#     def pause(self):
#         """Pauses the stopwatch if it is running, and adds the elapsed time to total_time."""
#         if self._running:
#             elapsed_time = time.time() - self._start_time  # Calculate elapsed time
#             self.total_time += elapsed_time  # Add elapsed time to the total time
#             self._running = False  # Set running flag to False
#             print(f"Stopwatch paused. Total time: {self.total_time:.2f} seconds.")
#         else:
#             print("Stopwatch is not running.")
#
#     def stop(self):
#         """Stops the stopwatch, adds any remaining time to total_time, and resets the stopwatch."""
#         if self._running:
#             self.pause()  # Pause the stopwatch to update the total time
#         self._start_time = None  # Reset the start time
#         print(f"Stopwatch stopped. Final time: {self.total_time:.2f} seconds.")
#
#     def return_total_time(self):
#         """Returns the total elapsed time in seconds."""
#         if self._running:
#             # If the stopwatch is running, calculate the current elapsed time
#             current_time = time.time() - self._start_time
#             return self.total_time + current_time
#         return float("{:.2f}".format(self.total_time))# Returns and formats the total elapsed time




class BidTimer:
    def __init__(self, timeout: int, callback):
        self.timeout = timeout
        self.callback = callback
        self.timer_task = None

    async def start(self):
        if self.timer_task:
            self.stop()
        self.timer_task = asyncio.create_task(self._run_timer())

    def stop(self):
        if self.timer_task:
            self.timer_task.cancel()
            self.timer_task = None

    async def _run_timer(self):
        try:
            await asyncio.sleep(self.timeout)
            await self.callback()
        except asyncio.CancelledError:
            pass