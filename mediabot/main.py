from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from aiohttp_swagger import setup_swagger
from telegram.ext import CommandHandler, MessageHandler, filters, Application


filterwarnings(action="ignore",message=r".*CallbackQueryHandler", category=PTBUserWarning)

# from mediabot.application import Application

application = Application()
setup_swagger(application.http_server, swagger_url="/api/docs")
http_server = application.http_server   
