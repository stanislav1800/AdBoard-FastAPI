from taskiq import InMemoryBroker, SmartRetryMiddleware
from taskiq_aio_pika import AioPikaBroker, Queue

from app.core.config import settings

retry_middleware = SmartRetryMiddleware(
    default_retry_count=settings.task_max_retries,
    default_delay=settings.task_retry_delay,
    use_jitter=True,
    use_delay_exponent=True,
    max_delay_exponent=settings.task_max_retry_delay,
)

if settings.environment == "pytest":
    broker = InMemoryBroker(await_inplace=True)
else:
    broker = AioPikaBroker(
        settings.rabbitmq_url,
        delay_queue=Queue(name="taskiq.delay"),
    ).with_middlewares(retry_middleware)
