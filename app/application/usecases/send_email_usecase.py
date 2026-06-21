
import asyncio
from app.domain.models import EmailPayload
from app.domain.errors import EmailSendError

class SendEmailUseCase:
    def __init__(self, sender_port):
        self._sender = sender_port

    def execute(self, payload: EmailPayload) -> str:
        """Execute send email use case."""
        # Try async method first (TokenManager), fallback to sync method
        if hasattr(self._sender, 'send_async'):
            try:
                # Run async method in event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, create a new task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._sender.send_async(payload))
                        return future.result()
                else:
                    return loop.run_until_complete(self._sender.send_async(payload))
            except Exception as e:
                # Fallback to sync method if async fails
                return self._sender.send(payload)
        else:
            return self._sender.send(payload)
