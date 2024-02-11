class Promise:
    def __init__(self):
        self.callbacks = []

    def then(self, callback):
        if not callable(callback):
            raise ValueError("Callback must be a function")

        self.callbacks.append(callback)

    async def resolve(self, value=None):
        for callback in self.callbacks:
            await callback(value)
