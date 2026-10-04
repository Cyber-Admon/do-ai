import logging
import os
import threading

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.filter import classify

log = logging.getLogger("do.slack")

TEST_MODE = os.environ.get("DO_TEST_REPLIES", "true").lower() == "true"


def build_app() -> App:
    app = App(token=os.environ["SLACK_BOT_TOKEN"])
    bot_user_id = app.client.auth_test()["user_id"]

    @app.event("app_mention")
    def on_mention(event, say):
        log.info("mention channel=%s", event.get("channel"))
        say(
            text="I'm here. Conversation is coming in the next step.",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )

    @app.event("message")
    def on_message(event, say):
        if event.get("bot_id") or event.get("subtype"):
            return

        text = event.get("text") or ""
        channel_type = event.get("channel_type")

        if channel_type == "im":
            log.info("dm received")
            say(text="I'm here. Conversation is coming in the next step.")
            return

        if f"<@{bot_user_id}>" in text:
            return

        decision = classify(text)
        log.info(
            "message channel=%s ts=%s decision=%s",
            event.get("channel"),
            event.get("ts"),
            decision,
        )

        if decision == "flagged" and TEST_MODE:
            say(
                text="Test mode: this looks like a request. "
                "Nothing has been sent anywhere.",
                thread_ts=event["ts"],
            )

    return app


def _run() -> None:
    try:
        handler = SocketModeHandler(build_app(), os.environ["SLACK_APP_TOKEN"])
        handler.start()
    except Exception:
        log.exception("Slack listener stopped")


def start_slack() -> None:
    if not (os.environ.get("SLACK_BOT_TOKEN") and os.environ.get("SLACK_APP_TOKEN")):
        log.warning("Slack tokens missing, listener not started")
        return
    threading.Thread(target=_run, daemon=True, name="slack-socket").start()