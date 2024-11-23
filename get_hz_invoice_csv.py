from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import pyotp

# Загрузка переменных из .env
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TWOFA_SECRET = os.getenv("TWOFA_SECRET")
COMPANY_NUMBER = "K0557577023"  # Укажите свой номер компании , взять можно из полседнего invoice

def apply_stealth(page):
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        window.navigator.chrome = {
            runtime: {},
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });
    """)

def extract_usage_link(page):
    """Извлекает ссылку для использования CSV"""
    links = page.query_selector_all('a.btn.btn-detail')
    for link in links:
        href = link.get_attribute('href')
        if href and "usage.hetzner.com" in href:
            return href
    return None

def main():
    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=True)

        # Создание контекста и страницы
        context = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = context.new_page()
        apply_stealth(page)

        # Авторизация
        page.goto('https://accounts.hetzner.com/login')
        page.type('input#_username', USERNAME) 
        page.type('input#_password', PASSWORD)
        page.click('input#submit-login')
        page.wait_for_load_state('load')

        # Обработка 2FA
        totp = pyotp.TOTP(TWOFA_SECRET)
        otp = totp.now()
        page.type("input#input-verify-code", otp)
        page.click("input#btn-submit")
        page.wait_for_load_state('load')

        # Переход на страницу счетов
        page.goto('https://accounts.hetzner.com/invoice')

        # Ожидание кнопок "Details"
        page.wait_for_selector('a.btn.btn-detail')

        # Извлечение ссылки
        usage_link = extract_usage_link(page)
        if not usage_link:
            print("Ссылка на usage.hetzner.com не найдена.")
            return

        print(f"Найдена ссылка на usage: {usage_link}")

        # Формирование ссылки для загрузки CSV
        csv_link = f"{usage_link}?csv&cn={COMPANY_NUMBER}"
        print(f"Ссылка для загрузки CSV: {csv_link}")

        # Скачивание CSV через page.request
        response = page.request.get(csv_link)
        if response.status != 200:
            print(f"Ошибка при скачивании CSV. Код: {response.status}")
            return

        # Сохранение файла
        file_path = "/tmp/invoice.csv"
        with open(file_path, "wb") as f:
            f.write(response.body())
        print(f"CSV файл загружен: {file_path}")

        # Закрытие браузера
        browser.close()

if __name__ == "__main__":
    main()
