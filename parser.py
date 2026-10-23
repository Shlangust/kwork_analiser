from time import sleep
from playwright.sync_api import sync_playwright
from excel import add_col
from config import acc_pass,acc_email
from contextlib import contextmanager
from playwright.sync_api import sync_playwright

@contextmanager
def main_session():
    """Открывает браузер, логинится и отдаёт page.
    После выхода из with браузер автоматически закрывается.
    """
    with sync_playwright() as p:
        page = enter(p)
        try:
            yield page
        finally:
            page.context.browser.close()
def enter(p):
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://kwork.ru/projects')

    page.click(".login-js")
    page.wait_for_selector(".auth-form")
    page.fill('input[type="text"][placeholder*="почта"]', acc_email)
    page.fill('input[type="password"]', acc_pass)
    page.click('button:has-text("Войти")')
    page.wait_for_load_state("networkidle")

    page.goto('https://kwork.ru/projects?fc=41')
    return page


def get_kworks(page):
    page.wait_for_selector('.want-card')
    projects_list = []
    cards = page.locator('.want-card').all()
    for card in cards:
        title = card.locator('.wants-card__header-title a').inner_text()
        desc_blocks = card.locator('.wants-card__description-text div.breakwords').all()
        if len(desc_blocks) > 1:
            description = desc_blocks[1].text_content()
        else:
            description = card.locator('.wants-card__description-text').first.text_content()
        cost = int(card.locator(".wants-card__price .d-inline").inner_text().replace(" ", "").replace("₽", "").strip())

        project_id = card.locator("h1.wants-card__header-title a").first.get_attribute("href").replace("projects","").replace("/","")
        projects_list.append({
            "title": title,
            "task": description,
            "cost": cost,
            "id":project_id,
            "link":f"https://kwork.ru/projects/{project_id}/view"
        })
    next_button = page.locator('.pagination__arrow.pagination__arrow--next')
    if next_button.count() > 0 and next_button.is_enabled():
        next_button.click()
        page.wait_for_selector('.want-card', state='attached')
        page.wait_for_timeout(1000)  # небольшая пауза для уверенности
        return projects_list + get_kworks(page)

    else:
        return projects_list

def get_kwork(page,link):
    page.goto(link)
    title = page.locator('.wants-card__header-title').inner_text()
    desc_blocks = page.locator('.wants-card__description-text div.breakwords').all()
    if len(desc_blocks) > 1:
        description = desc_blocks[1].text_content()
    else:
        description = page.locator('.wants-card__description-text').first.text_content()
    cost = int(page.locator(".wants-card__price .d-inline").inner_text().replace(" ", "").replace("₽", "").strip())

    project_data = {
        "title": title,
        "task": description,
        "cost": cost,
        "link" : link
    }
    next_button = page.locator('.pagination__arrow.pagination__arrow--next')
    if next_button.count() > 0 and next_button.is_enabled():
        next_button.click()
        page.wait_for_selector('.want-card', state='attached')
        page.wait_for_timeout(1000)  # небольшая пауза для уверенности
        return project_data + get_kworks(page)
    else:
        return project_data

def run_one_kwork(link):
    with sync_playwright() as p:
        enter_page = enter(p)
        kwork = get_kwork(enter_page, link)
        return kwork
