from unittest.mock import AsyncMock

import pytest

from app.tasks.email import EmailQueue, send_email_task


def test_email_task_retries_on_error():
    assert send_email_task.labels["retry_on_error"] is True

@pytest.mark.asyncio
async def test_email_queue_runs_task(monkeypatch):
    send = AsyncMock()
    monkeypatch.setattr("app.services.email.EmailService.send", send)

    await EmailQueue().send(recipients=["a@test.com"], subject="s", body="b")

    send.assert_awaited_once_with(recipients=["a@test.com"], subject="s", body="b")
