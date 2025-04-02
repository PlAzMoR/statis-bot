
import requests as r

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
# https://www.avito.ru/pavlovskiy_posad/predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&localPriority=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82
start_url = "https://www.avito.ru/"
end_url = "/predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82"
# end_url = "predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&localPriority=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82"
final_url = ""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.7",
}

# String to find in html response for taking paid ads amount
paid_ad_marker = '<i class="style-vas-icon-oH7rC style-vas-icon_type-promoted-wljDW style-vas-icon_size-xxs-YC_2S style-vas-icon_muted-M6t5W"></i>'
ads_amount_marker = 'data-marker="page-title/count">'
ad_item_marker = 'data-marker="item"'
my_ad_position_marker = "Любава Трофимова"

# https://www.avito.ru/brands/tga/items/all/predlozheniya_uslug?s=profile_search_show_all&sellerId=2d8c56b14c9e8ac30545616b4ac5b122


session = r.Session()
session.headers.update(headers)
response = session.get(start_url + cities.get("Павловский Посад") + end_url)

# ads_amount_marker_index = response.text.index(ads_amount_marker) + len(ads_amount_marker)

# print(help(response))

def get_ads_amount(response):
    ads_amount = ""
    ads_amount_index = response.text.index(ads_amount_marker) + len(ads_amount_marker)
    for i in range(10):
        char = response.text[ads_amount_index + i]
        if char == "<":
            return ads_amount
        ads_amount += char

def get_paid_ads_amount(response):
    return response.text.count(paid_ad_marker)

def get_my_ad_position(response):
    start_index = response.text.index(ad_item_marker) + len(ad_item_marker)
    is_my_ad_paided = False
    for position in range(50):
        end_index = response.text.index(ad_item_marker, start_index)
        print(f"{position}: {start_index} - {end_index}")
        # Return iterating position if position was spotted
        try:
            if response.text.index(my_ad_position_marker, start_index, end_index):
                if response.text.index(paid_ad_marker, start_index, end_index):
                    is_my_ad_paided = True
                return (position + 1, is_my_ad_paided)
        except ValueError:
            pass
        start_index = end_index + len(ad_item_marker)
    return (-1, is_my_ad_paided)

def get_page_statistics(session, city):
    url = start_url + cities.get(city) + end_url
    response = session.get(url)
    if response.status_code != 200:
        print(f"Error occured! Status code - {response.status_code}")
        return
    ads_amount = get_ads_amount(response)
    paid_ads_amount = get_paid_ads_amount(response)
    my_ad_position = get_my_ad_position(response)[0]
    is_my_ad_paided = get_my_ad_position(response)[1]
    print(f"Статистика по городу '{city}' (запрос 'юрист'): \nКол-во объявлений: {ads_amount} \nКол-во платников: {paid_ads_amount} \nПозиция нашего объявления: {my_ad_position} \nПроплачено ли объявление: {is_my_ad_paided}")


get_page_statistics(session=session, city="Коломна")
# print(get_my_ad_position(response=response))
# print(response.is_redirect)
