from telebot import TeleBot
from telebot.types import (
    Message,
    CallbackQuery,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    MenuButtonCommands,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from App.Components.Queries import Queries
from App.Components._MainMenu import _MainMenu
from App.Database.DB import DB
from App.Config.config import *
from App.Config.secrets import *
from App.Utils.Markup import Markup

# Import Models
from App.Database.users import User

# Import Components
from App.Components.main_menu import MainMenu

# Another packages
import json
import importlib

# Define bot
bot = TeleBot(BOT_TOKEN)


# Set basic commands (start, about, help)
basic_commands = [
    BotCommand("start", "🤖 Inicia o bot"),
    BotCommand("about", "❓ About the bot"),
    BotCommand("help", "📚 Help")
]
bot.set_my_commands(basic_commands, scope = BotCommandScopeAllPrivateChats() )
bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))


# WebApp messages handler
@bot.message_handler(content_types="web_app_data")
def answer_web_app_data(msg):
    userid = msg.from_user.id
    try:
        response = json.loads(msg.web_app_data.data)
        # clear keyboard
        bot.send_message(msg.from_user.id, 'Success! Data received: \n\n' + str(response), reply_markup=Markup.clear_markup())

        action = response.get('action')

        if action == 'main_menu':
            MainMenu(bot=bot, userid=userid)

    except Exception as e:
        print("#Error", e)
        # get line of error
        import traceback
        traceback.print_exc()

        response = msg.web_app_data.data
        bot.send_message(msg.from_user.id, 'Error, but data: \n\n' + response)


# /test command
@bot.message_handler(commands=['test'])
def teste(msg):
    userid = msg.chat.id
    bot.send_message(userid, 'Test')

def automatic_run(data_text: str, chat_id: int, call: CallbackQuery = None):
    """Padrão de chamada:
        /caminho_da_classe__metodo__parametro1__parametro2__parametro3
        
        - caminho_da_classe: Caminho da classe a ser chamada, isto é, pode estar dentro de um diretório e subdiretórios.
        - metodo: Método a ser chamado dentro da classe.
        - parametros: Parâmetros a serem passados para o método.
    """
    try:
        class_path, method_name, *params = data_text.split("__")
        class_name = class_path.split("_")[-1]
        class_path = ".".join([class_part for class_part in class_path.split("_")])
        method_name = f"{method_name}" if method_name else "async_init"
        print(f"\n  Class path: ", class_path, " | Class name: " + class_name + " | Método: ", method_name, " | Parâmetros: ", params)
    
        # Importar o módulo dinamicamente
        try:
            module = importlib.import_module(f"App.Components._{class_path}")
        except ModuleNotFoundError:
            try:
                module = importlib.import_module(f"App.Components.{class_path}.{class_path}")
            except ModuleNotFoundError:
                module = importlib.import_module(f"App.Components.{class_path}")
    
        # Obter a classe dinamicamente
        class_ = getattr(module, class_name)
    
        # Instanciar a classe
        instance = class_(bot, chat_id, call)

        # Obter o método dinamicamente e chamá-lo com os parâmetros
        method = getattr(instance, method_name)
        method(*params)
        return

    except Exception as e:
        # bot.send_message(chat_id, 'Oops! Ocorreu um erro inesperado ao executar o comando. Contate o suporte.')
        bot.send_message(chat_id, 'Opa, calma aí, paizão. Tô desenvolvendo isso ainda. Mas já já tá pronto. \n Ou talvez é só um comando desconhecido mesmo haha')
        text_erro = f"Erro inesperado: {e} \n Linha: {e.__traceback__.tb_lineno}"
        print(text_erro + '\n\n\n')
        raise e
        return

# Any message
@bot.message_handler(func= lambda m: True)
def receber(msg: Message):
    userid = msg.from_user.id
        
    if msg.text == "/about":
        bot.send_message(userid, "About the bot")
        msg_about = "This bot is template a bot that uses the WebApp feature (Mini App).\n\n"
        msg_about += "Source code: "
        bot.send_message(userid, msg_about)
        return
    
    elif msg.text == "/help":
        bot.send_message(userid, "Help")
        msg_help = "Commands:\n"
        msg_help += "/start - Start the bot\n"
        msg_help += "/about - About the bot\n"
        msg_help += "/help - Help\n"
        bot.send_message(userid, msg_help)
        return
    
    elif msg.text.startswith("/get_media_"):
        media_id = msg.text.split("_")[2]
        bot.copy_message(userid, '-1002215339038', media_id)
    
    if msg.text.startswith("/") and not msg.text.startswith("/start"):
        automatic_run(msg.text[1:], userid)
        return

    # MainMenu(bot=bot, userid=userid)
    _MainMenu(bot, userid)

    # # Verify if user exists
    # if db.verify_user(userid) == False:
    #     db.add_user(userid, user.first_name, user.username, user.language_code.split('-')[0] )


# CALLBACKS
@bot.callback_query_handler(func=lambda call: call.data.startswith('_') == False) # call_data starting with * is for components
def callback(call):
    userid = call.from_user.id
    data = call.data

    options = {
        'hello': lambda: bot.answer_callback_query(call.id, f'Olá {call.from_user.first_name}'),
        'start_from_here': lambda: MainMenu(bot, userid, call, MainMenu.start_from_here)
    }

    if data in options:
        options[data]() # Executes the function in the dict
    else:
        automatic_run(data, userid, call)


@bot.inline_handler(lambda query: True)
def inline_handler(query: InlineQuery):
    # try:
    #     query_patterns = {
    #         'nome_obra:'
    #     }
    #     r = InlineQueryResultArticle('1', 'Result', InputTextMessageContent('Result message'))
    #     # r2 = InlineQueryResultArticle('1', 'Result', InputPhotoResult('Result message'))
    #     bot.answer_inline_query(query.id, [r])
    # except Exception as e:
    #     print(e)
    
    # resultados = Queries(bot).pesquisar_obras(query.query)
    resultados = Queries(bot, query.query).get_results()
    bot.answer_inline_query(query.id, results=resultados, cache_time=1)

    pass


bot.infinity_polling()