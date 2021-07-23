class TaskerError(Exception): pass

class Tasker:
    def __init__(self, task_name: str) -> None:
        self.name = task_name
        self.args = None
    
    def preload(self) -> None:
        pass
    
    async def start(self) -> None:
        pass

    def end(self) -> None:
        pass
