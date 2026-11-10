import logging

from app.services.email import EmailService
from app.tasks.broker import broker

logger = logging.getLogger(__name__)


@broker.task(task_name="email.send", retry_on_error=True)
async def send_email_task(recipients: list[str], subject: str, body: str):
    """
    Отправка письма воркером. При ошибке SMTP задача повторяется
    с нарастающей задержкой (SmartRetryMiddleware).
    """
    await EmailService().send(recipients=recipients, subject=subject, body=body)
    logger.info("Письмо '%s' отправлено: %s", subject, recipients)


class EmailQueue:
    """
    Постановка писем в очередь. Сервисы зависят от неё, а не от SMTP:
    письмо не теряется при рестарте приложения и не тормозит запрос.
    """

    async def send(self, recipients: list[str], subject: str, body: str):
        await send_email_task.kiq(recipients=recipients, subject=subject, body=body)


def get_email_queue() -> EmailQueue:
    return EmailQueue()
