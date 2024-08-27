from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo
)
from .functions import dict_to_url_params

class Markup():

    @staticmethod
    def generate_inline(buttons: list, sufix: str = ''):
        """
        Generates an inline keyboard markup using the provided buttons.

        Args:
            buttons (list): A list of buttons in the format:
            [ # scope
                [ # line
                    ['Butto1', 'action1'], # button
                    ['Butto2', 'action2'],
                ],
                [
                    ['Butto3', 'action3'],
                    ['Butto4', 'action4'],
                    ['Butto5', 'action5']
                ]
            ]
            sufix (str, optional): A suffix to be added to the callback data. Defaults to ''.

        Returns:
            InlineKeyboardMarkup: The generated inline keyboard markup.
        """
        keyboard = InlineKeyboardMarkup()
        for row in buttons:
            row_buttons = []
            for button in row:
                row_buttons.append(
                    InlineKeyboardButton(text=button[0], callback_data=f'{button[1]}{sufix}')
                )
            keyboard.row(*row_buttons)
        return keyboard
    
    @staticmethod
    def generate_keyboard(buttons: list, **kwargs) -> ReplyKeyboardMarkup:
        """ Example:
        buttons = [
            ['Button1', 'Button2'],
            ['Button3', 'Button4', 'Button5']
        ]
        """
        keyboard = []
        for line in buttons:
            linha = []
            for button in line:
                linha.append(KeyboardButton(button))
            keyboard.append(linha)
            
        print('Keyboard Buttons: ', keyboard)
        return ReplyKeyboardMarkup(keyboard=keyboard, **kwargs)
    
    @staticmethod
    def clear_markup():
        return ReplyKeyboardRemove()
    
    @staticmethod
    def cancelar_keyboard():
        return Markup.generate_keyboard([['CANCELAR']])
   