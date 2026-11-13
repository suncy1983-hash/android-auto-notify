"""Constants for Android Auto értesítések."""

DOMAIN = "android_auto_notify"

CONF_WEBHOOK_ID = "webhook_id"
CONF_EXCLUDE = "exclude"

# Companion app commands sent as the message text. They are not visible
# notifications, so they are passed through untouched.
COMMAND_MESSAGES = {
    "clear_notification",
    "remove_channel",
    "request_location_update",
    "update_sensors",
    "TTS",
}
COMMAND_PREFIX = "command_"
