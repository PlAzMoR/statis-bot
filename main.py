
import requests as r
from bs4 import BeautifulSoup


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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

# Returns ads list
def get_ads_list(soup: BeautifulSoup) -> BeautifulSoup:
    item_catalog = soup.find('div', attrs={'data-marker':'catalog-serp'})
    return item_catalog.find_all('div', attrs={'data-marker':'item'})

# Returns total ads amount
def get_ads_amount(soup: BeautifulSoup) -> int:
    return soup.find('span', attrs={'data-marker':'page-title/count'}).text


# Returns ad name
def get_ad_name(ad: BeautifulSoup) -> str:
    return ad.find('h3', attrs={'itemprop':'name'}).text

# Returns ad author (returns None if no author given in html)
def get_ad_author(ad: BeautifulSoup) -> str:
    author_marker = "styles-module-root-s4tZ2 styles-module-size_s-nEvE8 styles-module-size_s_compensated-wyNaE " \
                    "styles-module-size_s-PDQal styles-module-ellipsis-A5gkK styles-module-ellipsis_oneLine-xwEfT " \
                    "stylesMarningNormal-module-root-_xKyG stylesMarningNormal-module-paragraph-s-HX94M"
    author = ad.find('p', attrs={'class':author_marker})
    if author is not None:
        return author.text
    return None

# Returns True if given ad is paided, False otherwise
def get_ad_payment(ad: BeautifulSoup) -> bool:
    payment_marker = "style-vas-icon-oH7rC style-vas-icon_type-promoted-wljDW style-vas-icon_size-xxs-YC_2S style-vas-icon_muted-M6t5W"
    if ad.find('i', attrs={'class':payment_marker}):
        return True
    return False

# Saves response html to file
def save_html(response: str) -> None:
    with open('response.html', 'w', encoding='utf-8') as html:
        html.write(response)

# Returns tuple with given city ads statistics
def get_page_statistics(session: r.Session, city_url: str) -> tuple:
    url = start_url + city_url + end_url
    response = session.get(url)

    # Bad status error handler
    if response.status_code != 200:
        print(f"Error occured! Status code - {response.status_code}")
        return

    # save_html(response=response)
    soup = BeautifulSoup(response.text, 'html.parser')

    paid_ads_flag = True
    ads_amount = get_ads_amount(soup=soup)
    first_paid_ads_amount = 0
    total_paid_ads_amount = 0
    is_my_ad_paided = False
    my_ad_position = -1

    # Iterating every ad in response to find correct marker in it
    for i, item in enumerate(get_ads_list(soup=soup), 1):

        if get_ad_payment(ad=item) == True:
            total_paid_ads_amount += 1
            if paid_ads_flag == True:
                first_paid_ads_amount += 1
        else:
            paid_ads_flag = False

        if get_ad_author(ad=item) == "Любава Трофимова":
            my_ad_position = i
            if get_ad_payment(ad=item) == True:
                is_my_ad_paided = True

    # print(f"{city_url} --- {ads_amount} / {first_paid_ads_amount} / {my_ad_position} / {is_my_ad_paided}")
    return (url, ads_amount, total_paid_ads_amount, first_paid_ads_amount, my_ad_position, is_my_ad_paided)

# Prints all cities statistics to console
def print_total_statistics(cities_dict: dict) -> None:
    session = r.Session()
    session.headers.update(headers)
    print("Статистика считывается...")
    print("Город - Кол-во объявлений / Кол-во платников (всего) / Кол-во платников (подряд) / Наше место / Платное ли наше объявление?")
    for city, city_url in cities_dict.items():
        page_result = get_page_statistics(session=session, city_url=city_url)
        print(f"{city} - {page_result[1]} / {page_result[2]} / {page_result[3]} / {page_result[4]} / {page_result[5]} ----- {page_result[0]}")

print_total_statistics(cities_dict=cities)
