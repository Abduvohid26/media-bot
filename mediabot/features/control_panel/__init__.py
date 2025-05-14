from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from mediabot.features.control_panel.handlers import control_panel_handle_control_panel_callback_query, control_panel_handle_control_panel_command, \
    control_panel_handle_set_admin_command, control_panel_handle_set_bot_name_command, control_panel_handle_statistics_callback_query, control_panel_handle_unset_admin_command

class ControlPanelFeature:
  control_panel_command_handler = CommandHandler("control_panel", control_panel_handle_control_panel_command)
  control_panel_callback_query_handler = CallbackQueryHandler(control_panel_handle_control_panel_callback_query, "control_panel")

  control_panel_set_admin_command_handler = CommandHandler("set_admin", control_panel_handle_set_admin_command)
  control_panel_unset_admin_command_handler = CommandHandler("unset_admin", control_panel_handle_unset_admin_command)
  control_panel_set_bot_name_command_handler = CommandHandler("set_bot_name", control_panel_handle_set_bot_name_command)

  control_panel_statistics_callback_query_handler = CallbackQueryHandler(control_panel_handle_statistics_callback_query, "^statistics$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(ControlPanelFeature.control_panel_command_handler)
    botapp.add_handler(ControlPanelFeature.control_panel_callback_query_handler)
    botapp.add_handler(ControlPanelFeature.control_panel_set_admin_command_handler)
    botapp.add_handler(ControlPanelFeature.control_panel_unset_admin_command_handler)
    botapp.add_handler(ControlPanelFeature.control_panel_set_bot_name_command_handler)
    botapp.add_handler(ControlPanelFeature.control_panel_statistics_callback_query_handler)
