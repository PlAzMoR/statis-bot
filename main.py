
import requests as r
import bs4

cities = {
    "Домодедово": "domodedovo",
    "Подольск": "podolsk",
    "Сергиев Посад": "sergiev_posad",
    "Обнинск": "obninsk",
    "Балашиха": "balashiha",
    "Мытищи": "mytischi",
    "Видное": "vidnoe",
    "Люберцы": "lyubertsy",
    "Химки": "himki",
    "Пушкино": "pushkino",
    "Королёв": "korolev",
    "Серпухов": "serpuhov",
    "Павловский Посад": "pavlovskiy_posad",
    "Зеленоград": "moskva_zelenograd",
    "Щёлково": "schelkovo",
    "Одинцово": "odintsovo",
    "Ногинск": "noginsk",
    "Раменское": "ramenskoe",
    "Электросталь": "elektrostal",
    "Жуковский": "zhukovskiy",
    "Солнечногорск": "solnechnogorsk",
    "Красногорск": "moskovskaya_oblast_krasnogorsk",
    "Долгопрудный": "dolgoprudnyy",
    "Коломна": "kolomna"
}

start_url = "https://www.avito.ru/"
end_url = "/predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.7",
}

markers = {
    "paid_ad": '<i class="style-vas-icon-oH7rC style-vas-icon_type-promoted-wljDW style-vas-icon_size-xxs-YC_2S style-vas-icon_muted-M6t5W"></i>',
    "ads_amount": 'data-marker="page-title/count">',
    "ad_item": 'data-marker="item"',
    "my_ad_position": "Любава Трофимова"
}

# https://www.avito.ru/brands/tga/items/all/predlozheniya_uslug?s=profile_search_show_all&sellerId=2d8c56b14c9e8ac30545616b4ac5b122


# Returns value of ads amount in given response
def get_ads_amount(response):
    ads_amount = ""
    ads_amount_index = response.text.index(markers.get("ads_amount")) + len(markers.get("ads_amount"))

    # Iterating chars in the found number (10 chars max) and copying to string
    for i in range(10):
        char = response.text[ads_amount_index + i]
        if char == "<":
            break
        ads_amount += char

    return int(ads_amount)
        

# Returns value of paid ads amount in given response
def get_paid_ads_amount(response):
    return response.text.count(markers.get("paid_ad"))

# Returns tuple with first value - my ad position, second one - is my ad paided
def get_my_ad_position(response):
    start_index = response.text.index(markers.get("ad_item")) + len(markers.get("ad_item"))
    is_my_ad_paided = False

    # Iterating every ad in response to find correct marker in it
    for position in range(49):
        end_index = response.text.index(markers.get("ad_item"), start_index)
        # Return iterating position if marker was spotted
        try:
            if response.text.index(markers.get("my_ad_position"), start_index, end_index):
                # Checking if my ad is paided
                if response.text.index(markers.get("paid_ad"), start_index, end_index):
                    is_my_ad_paided = True
                return (position + 1, is_my_ad_paided)
        # Marker-not-found exception
        except ValueError:
            pass
        start_index = end_index + len(markers.get("ad_item"))
    # Returns -1 if my ad wasn't found on first page
    return (-1, is_my_ad_paided)

# Returns tuple with given city page values like this (city_url, ads_amount, paid_ads_amount, my_ad_position, is_my_ad_paided)
def get_page_statistics(session, city_url):
    url = start_url + city_url + end_url
    response = session.get(url)
    # Get response error handler
    if response.status_code != 200:
        print(f"Error occured! Status code - {response.status_code}")
        return
    # Collecting all page values
    ads_amount = get_ads_amount(response)
    paid_ads_amount = get_paid_ads_amount(response)
    my_ad_position, is_my_ad_paided = get_my_ad_position(response)
    return (url, ads_amount, paid_ads_amount, my_ad_position, is_my_ad_paided)

# Prints all cities statistics to console
def print_total_statistics(cities_dict):
    session = r.Session()
    session.headers.update(headers)
    # print("Статистика считывается...")
    print("Город - Кол-во объявлений / Кол-во платников / Наше место / Платное ли наше объявление?")
    for city, city_url in cities_dict.items():
        page_result = get_page_statistics(session=session, city_url=city_url)
        print(f"{city} - {page_result[1]} / {page_result[2]} / {page_result[3]} / {page_result[4]} ----- {page_result[0]}")

print_total_statistics(cities_dict=cities)

