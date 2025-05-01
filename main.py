
from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright
from time import sleep

# Dict of cities url insertion
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

# Urls to concatenate with city-url from dict
start_url = "https://www.avito.ru/"
end_url = "/predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&localPriority=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82"
end_url_no_local = "/predlozheniya_uslug/delovye_uslugi-ASgBAgICAUSYC7KfAQ?cd=1&q=%D1%8E%D1%80%D0%B8%D1%81%D1%82"


# Returns city of current page by url
def get_page_city(page) -> str:
    url = page.url
    url = url[len(start_url)-1:]
    url = url[:url.find('/')]
    return url
    # return page.query_selector('span[class="buyer-pages-mfe-location-nev1ty"]').inner_text()

# Returns ads amount on page
def get_ads_amount(page) -> int:
    return int(page.query_selector('span[data-marker="page-title/count"]').inner_text())

# Returns name of given ad
def get_ad_name(ad) -> str:
    return ad.query_selector('a[data-marker="item-title"]').inner_text()

# Return author of given ad
def get_ad_author(ad) -> str:
    author_selector = 'p[class="styles-module-root-PY1ie styles-module-size_m-w6vzl styles-module-size_m_dense-HvBLt ' \
                    'styles-module-size_m_compensated-a0qNK styles-module-size_m-DKJW6 styles-module-ellipsis-HCaiF ' \
                    'styles-module-ellipsis_oneLine-VXBA3 styles-module-size_dense-u0sRJ stylesMarningNormal-module-root-OE0X2 ' \
                    'stylesMarningNormal-module-paragraph-m-dense-mYuSK"]'

    author_tag = ad.query_selector(author_selector)

    if author_tag is not None:
        return author_tag.inner_text()
    return ''

# Returns True if given ad is paided, False otherwise
def get_ad_payment(ad) -> bool:
    payment_selector = 'span[class="styles-module-noAccent-nSgNq"]'

    if ad.query_selector(payment_selector):
        return True
    return False


# Returns parsed stats from given city page
def get_page_statistics(page, city_url: str) -> list:
    url = start_url + city_url + end_url
    page.goto(url=url)

    ads_amount = get_ads_amount(page=page)
    my_ad_position = -1
    paid_ads_amount_first = 0
    paid_ads_amount_first_flag = True
    paid_ads_amount_total = 0
    is_my_ad_paided = False

    catalog = page.query_selector('div[data-marker="catalog-serp"]')
    items = catalog.query_selector_all('div[data-marker="item"]')

    for i, item in enumerate(items, 1):
        # Srolling to item to ensure it fully loaded
        item.scroll_into_view_if_needed()

        # Taking payment values
        if get_ad_payment(ad=item) == True:
            paid_ads_amount_total += 1
            if paid_ads_amount_first_flag:
                paid_ads_amount_first += 1
        else:
            paid_ads_amount_first_flag = False

        # Taking my position
        if get_ad_author(ad=item) == "Любава Трофимова":
            my_ad_position = i
            if get_ad_payment(ad=item) == True:
                is_my_ad_paided = True

    # return {'city_url': city_url, 'ads_amount': ads_amount, 'my_ad_position': my_ad_position, 'is_my_ad_paided': is_my_ad_paided,
    #         'paid_ads_amount_first': paid_ads_amount_first, 'paid_ads_amount_total': paid_ads_amount_total}
    return [city_url, ads_amount, my_ad_position, is_my_ad_paided, paid_ads_amount_first, paid_ads_amount_total]


# Initializes headful browser. Returns new blank page
def browser_initialize(playwright, debug: bool):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    launch_args = ['--disable-blink-features=AutomationControlled', '--window-size=900,700']
    state = None

    if not debug:
        launch_args.append('--window-position=9999,9999')

    # Starting browser with some args
    browser = playwright.chromium.launch(headless=False, args=launch_args)
    context = browser.new_context(no_viewport=True, user_agent=user_agent, storage_state=state)
    page = context.new_page()

    def block_heavy_content(route):
        if route.request.resource_type in ['image', 'font', 'stylesheet']:
            route.abort()
        else:
            route.continue_()

    # Skipping heavy data in no-debug mode
    if not debug:
        page.route('**/*', block_heavy_content)

    return page


def print_percentage(max_elements: int, current_element: int, round_factor: int = 1) -> None:
    print(f'\r{round((100 / max_elements) * current_element, round_factor)}%', end='')

# Returns all cities statistics
def get_total_statistics(playwright, cities: dict, show_percentage: bool, debug: bool = False) -> dict:
    page = browser_initialize(playwright=playwright, debug=debug)
    total_stats = {}
    index = 0

    # Iterating stats for every city
    for city, city_url in cities.items():
        total_stats[city] = get_page_statistics(page=page, city_url=city_url)

        index += 1
        if show_percentage: print_percentage(max_elements=len(cities), current_element=index)

    return total_stats

def save_statistics(total_stats: dict, path: str) -> None:
    with open(file=path, mode='w') as file:
        file.write(str(total_stats))

def load_statistics(path: str) -> dict:
    with open(file=path, mode='r') as file:
        return dict(file.read())

# Prints total statistics to console. Accepts position list of values to print (0 - dont print) in sequence:
# city_url, ads_amount, my_ad_position, is_my_ad_paided, paid_ads_amount_first, paid_ads_amount_total
def print_total_statisctics(total_stats: dict, values_position_list: list) -> None:

    for city, city_stats in total_stats:
        print(f'{city} - ', end='')

        printable_list = [0] * len(values_position_list)
        for i, pos in enumerate(values_position_list):
            if pos != 0:
                printable_list[pos] = city_stats[i]
        print(printable_list)

# Prints total statistics to console by default sequence
def print_total_statistics_default(total_stats: dict) -> None:
    print('Город - Кол-во объявлений / Кол-во платников (подряд) / Моя позиция / Платное ли мое объявление?')
    for city, city_stats in total_stats:
        print(f'{city} - {city_stats[1]} / {city_stats[4]} / {city_stats[2]} / {city_stats[3]}')


if __name__ == '__main__':
    with sync_playwright() as p:
        print_total_statistics_default(get_total_statistics(playwright=p, cities=cities, show_percentage=True, debug=True))
