import time

import heapq
import time

class Task:
    def __init__(self, name, execution_time, deadline):
        self.name = name
        self.execution_time = execution_time
        self.deadline = deadline
        self.remaining_time = execution_time
        self.start_time = time.time()
    
    def slack_time(self):
        return self.deadline - (time.time() - self.start_time)
    
    def __lt__(self, other):
        return self.slack_time() < other.slack_time()
    
    def __repr__(self):
        return (f"Task(name={self.name}, execution_time={self.execution_time}, "
                f"deadline={self.deadline}, remaining_time={self.remaining_time}, "
                f"slack_time={self.slack_time()})")


class LSF_Scheduler:
    def __init__(self):
        self.task_queue = []
    
    def add_task(self, task):
        heapq.heappush(self.task_queue, task)
    
    def get_next_task(self):
        if self.task_queue:
            return heapq.heappop(self.task_queue)
        return None
    
    def run(self):
        while self.task_queue:
            task = self.get_next_task()
            print(f"Running task: {task.name}")
            start_time = time.time()
            time.sleep(task.execution_time)  # Simulate task execution
            task.remaining_time = 0
            print(f"Completed task: {task.name}")
            if task.slack_time() > 0:
                self.add_task(task)  # Re-add task if there's slack time remaining