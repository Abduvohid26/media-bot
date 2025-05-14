from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from mediabot.features.sys.handlers import sys_handle_backup, sys_handle_bootstrap_callback_query, sys_handle_db_conn_pool_info, sys_handle_db_stat_activity_info, sys_handle_features_command, \
    sys_handle_info, sys_handle_pending_updates, sys_handle_reset_pending_updates, sys_handle_sync_commands, sys_handle_toggle_feature, \
    sys_handle_bootstrap, sys_handle_feature_toggle_callback_query

class SysFeature:
  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(CommandHandler("sys_info", sys_handle_info))
    botapp.add_handler(CommandHandler("sys_db_conn_pool_info", sys_handle_db_conn_pool_info))
    botapp.add_handler(CommandHandler("sys_db_stat_activity_info", sys_handle_db_stat_activity_info))
    botapp.add_handler(CommandHandler("sys_backup", sys_handle_backup))
    botapp.add_handler(CommandHandler("sys_sync_commands", sys_handle_sync_commands))
    # botapp.add_handler(CommandHandler("sys_reset_webhook", sys_handle_reset_webhook))
    botapp.add_handler(CommandHandler("sys_pending_updates", sys_handle_pending_updates))
    botapp.add_handler(CommandHandler("sys_reset_pending_updates", sys_handle_reset_pending_updates))
    botapp.add_handler(CommandHandler("sys_toggle_feature", sys_handle_toggle_feature))
    botapp.add_handler(CommandHandler("sys_bootstrap", sys_handle_bootstrap))
    botapp.add_handler(CommandHandler("sys_features", sys_handle_features_command))
    botapp.add_handler(CallbackQueryHandler(sys_handle_feature_toggle_callback_query, "^sys_feature_([a-zA-Z0-9_-]+)_([on|off]+)$"))
    botapp.add_handler(CallbackQueryHandler(sys_handle_bootstrap_callback_query, "^sys_bootstrap$"))
