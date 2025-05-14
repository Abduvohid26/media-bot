from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class ControlPanelKeyboardMarkup:
  @staticmethod
  def build(advertisement_count: int, broadcast_count: int, command_count: int, \
      language_count: int, required_join_count: int, referral_count: int, join_request_chat_count: int) -> InlineKeyboardMarkup:

    control_panel_buttons = [
      [
        InlineKeyboardButton(f"📑️ Advertisements ({advertisement_count})", callback_data="advertisement"),
        InlineKeyboardButton(f"📯️ Broadcasts ({broadcast_count})", callback_data="broadcast")
      ],
      [
        InlineKeyboardButton(f"🗃 Commands ({command_count})", callback_data="command"),
        InlineKeyboardButton(f"👤 Join requests ({join_request_chat_count})", callback_data="join_requests"),
      ],
      [
        InlineKeyboardButton(f"🗣 Languages ({language_count})", callback_data="language"),
        InlineKeyboardButton(f"🚪 Required joins ({required_join_count})", callback_data="required_join"),
      ],
      [
        InlineKeyboardButton(f"🧵 Referrals ({referral_count})", callback_data="referral"),
        InlineKeyboardButton(f"📊 Statistics", callback_data="statistics"),
      ],
    ]

    return InlineKeyboardMarkup(control_panel_buttons)
