import telebot
import requests
from settings import *
import json

bot = telebot.TeleBot(TOKEN)
keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
keyboard.add(telebot.types.KeyboardButton("Что посмотреть?"))
keyboard.add(telebot.types.KeyboardButton("О проекте"))

@bot.message_handler(commands=['start', 'help'])
def start_message(message) -> None:
    bot.send_message(message.chat.id, START_MESSAGE, reply_markup=keyboard)

@bot.message_handler(regexp='О Проекте')
def about(message) -> None:
    bot.send_message(message.chat.id, ABOUT_MESSAGE)

@bot.message_handler(regexp='Что посмотреть?')
def advice_film(message) -> None:
    bot.send_message(message.chat.id, "Ищу...")
    film_data = get_random_film()
    if isinstance(film_data, str):
        bot.send_message(message.chat.id, f"Ошибка! {json.loads(film_data)['message']}")
        return
    bot.send_photo(message.chat.id, film_data['poster_url'])
    response = f"""
    Название: {film_data['name']} ({film_data['year']})\n\
Жанр: {film_data['genres']}\n\
Рейтинг Кинопоиска: {film_data['rating_kp']}\n\
Рейтинг IMDB: {film_data['rating_imdb']}\n\
Описание: {film_data['description'] if film_data['description'] != "None" else "Не найдено"}
    """
    bot.send_message(message.chat.id, response)

def get_random_film() -> dict | str:
    url = 'https://api.kinopoisk.dev/v1/movie/random'
    headers = {
        'accept': 'application/json',
        'X-API-KEY': API_KEY_TO_KINOPOISK}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        genres = data['genres']
        categories = []
        for genre in genres:
            categories.append(*genre.values())
        categories = ', '.join(categories)
        
        ratings = data['rating']
        film_data = {
            'name': data['name'],
            'description': data['description'],
            'year': data['year'],
            "poster_url": data['poster']['url'],
            "genres": categories.title(),
            "rating_kp": ratings['kp'],
            "rating_imdb": ratings['imdb']
        }
        return film_data
    else:
        return response.text
    
bot.infinity_polling()