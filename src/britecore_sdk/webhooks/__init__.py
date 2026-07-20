"""Webhook event handler framework for real-time BriteCore events.

Provides a framework for receiving and handling webhook events from the BriteCore API.
"""

import hashlib
import hmac
import json
from collections.abc import Callable
from typing import Any

from britecore_sdk import logger


class WebhookEvent:
    """Represents a webhook event from BriteCore."""

    def __init__(self, event_type: str, data: dict[str, Any], timestamp: str):
        """Initialize webhook event.

        Args:
            event_type: Type of event (e.g., "policy.created", "quote.updated").
            data: Event payload data.
            timestamp: Event timestamp.
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"WebhookEvent(type={self.event_type}, timestamp={self.timestamp})"


class WebhookListener:
    """Webhook event listener and handler.

    Example::

        listener = WebhookListener(secret="your-webhook-secret")

        @listener.on("policy.created")
        def handle_policy_created(event):
            print(f"New policy: {event.data['policy_id']}")

        listener.start(port=8000)
    """

    def __init__(self, secret: str, logger_instance=None):
        """Initialize webhook listener.

        Args:
            secret: Webhook secret for signature verification.
            logger_instance: Logger instance to use (uses SDK logger if None).
        """
        self.secret = secret
        self.logger = logger_instance or logger
        self.handlers: dict[str, list[Callable[[WebhookEvent], None]]] = {}
        self._running = False

    def on(self, event_type: str) -> Callable:
        """Decorator to register event handler.

        Args:
            event_type: Type of event to handle.

        Returns:
            Decorator function.

        Example::

            @listener.on("policy.created")
            def handle_creation(event):
                print(f"Policy created: {event.data}")
        """

        def decorator(func: Callable[[WebhookEvent], None]) -> Callable:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(func)
            return func

        return decorator

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature.

        Args:
            payload: Raw webhook payload.
            signature: Signature header from webhook request.

        Returns:
            True if signature is valid, False otherwise.
        """
        expected_signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> bool:
        """Process incoming webhook payload.

        Args:
            payload: Webhook payload data.
            signature: Optional signature for verification.

        Returns:
            True if processed successfully, False otherwise.
        """
        if signature and not self.verify_signature(json.dumps(payload), signature):
            self.logger.error("Webhook signature verification failed")
            return False

        event_type = payload.get("type")
        if not event_type:
            self.logger.error("Webhook payload missing event type")
            return False

        event = WebhookEvent(
            event_type=event_type,
            data=payload.get("data", {}),
            timestamp=payload.get("timestamp", ""),
        )

        # Call registered handlers
        handlers = self.handlers.get(event_type, [])
        if not handlers:
            self.logger.warning(f"No handlers registered for event type: {event_type}")
            return True

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error in webhook handler: {e}", exc_info=True)

        return True

    def start(self, port: int = 8000, host: str = "0.0.0.0") -> None:
        """Start webhook listener server.

        Args:
            port: Port to listen on (default 8000).
            host: Host to bind to (default 0.0.0.0).

        Note:
            This is a placeholder implementation. In production, you would use
            Flask, FastAPI, or another web framework.
        """
        self._running = True
        self.logger.info(f"Webhook listener would start on {host}:{port}")
        # Implementation would depend on web framework choice

    def stop(self) -> None:
        """Stop webhook listener."""
        self._running = False
        self.logger.info("Webhook listener stopped")


class WebhookManager:
    """Manage multiple webhook listeners and routes."""

    def __init__(self, secret: str):
        """Initialize webhook manager.

        Args:
            secret: Webhook secret.
        """
        self.secret = secret
        self.listeners = {}

    def create_listener(self, name: str) -> WebhookListener:
        """Create a named webhook listener.

        Args:
            name: Name for the listener.

        Returns:
            WebhookListener instance.
        """
        listener = WebhookListener(self.secret)
        self.listeners[name] = listener
        return listener

    def get_listener(self, name: str) -> WebhookListener | None:
        """Get a listener by name.

        Args:
            name: Listener name.

        Returns:
            WebhookListener or None if not found.
        """
        return self.listeners.get(name)


__all__ = [
    "WebhookEvent",
    "WebhookListener",
    "WebhookManager",
]
