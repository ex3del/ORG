import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
import json

# --- Конфигурация ---
BASE_URL = "http://ezboardgames.com"
# Страница 1 это /games/, последующие страницы /games/N/
START_PAGE = 1  # Представляет /games/
END_PAGE = 11  # Представляет /games/11/
DOWNLOAD_FOLDER = rf"C:\Users\777\Documents\ORG\rules"  # Папка для сохранения PDF
# Имя файла для JSON-лога с метаданными
METADATA_FILENAME = rf"C:\Users\777\Documents\ORG\rules\rules_metadata.json"
REQUEST_DELAY = 2  # Задержка в секундах между запросами для вежливости

# --- Вспомогательные функции ---


def sanitize_filename(filename):
    """
    Очищает строку, чтобы она стала валидным именем файла.

    Удаляет или заменяет символы, недопустимые в именах файлов в большинстве ОС,
    заменяет пробелы на подчеркивания и обрезает слишком длинные имена.
    Также гарантирует, что имя файла заканчивается на '.pdf'.

    Args:
        filename (str): Исходная строка (предполагаемое имя файла).

    Returns:
        str: Очищенная строка, подходящая для использования в качестве имени файла.
    """
    # Удаляем недопустимые символы
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Заменяем пробелы на подчеркивания
    sanitized = sanitized.replace(" ", "_")
    # Удаляем потенциальные строки запроса или фрагменты URL
    sanitized = sanitized.split("?")[0].split("#")[0]
    # Убеждаемся, что имя заканчивается на .pdf, если должно
    if not sanitized.lower().endswith(".pdf"):
        # Если исходное имя (после удаления query string) было PDF, сохраняем его
        original_base = os.path.basename(filename.split("?")[0].split("#")[0])
        if original_base.lower().endswith(".pdf"):
            # Попытка использовать оригинальное имя файла из URL, если оно заканчивается на .pdf
            sanitized = re.sub(r'[\\/*?:"<>|]', "", original_base).replace(" ", "_")
        else:
            sanitized += ".pdf"  # Добавляем .pdf, если его нет

    # Обрезаем слишком длинные имена файлов при необходимости
    return sanitized[:150]  # Ограничиваем длину чуть щедрее


def download_pdf(pdf_url, game_title, folder):
    """
    Скачивает PDF-файл по заданному URL и сохраняет его в указанную папку.

    Проверяет существование папки, формирует имя файла (предпочитая имя из URL,
    если оно похоже на PDF, иначе использует название игры), проверяет,
    не скачан ли файл уже. Выполняет GET-запрос, проверяет ответ и тип контента,
    затем сохраняет файл. Обрабатывает возможные ошибки сети и другие исключения.

    Args:
        pdf_url (str): URL для скачивания PDF-файла.
        game_title (str): Название игры (используется для формирования имени файла,
                          если не удалось получить его из URL).
        folder (str): Путь к папке, куда нужно сохранить файл.

    Returns:
        tuple[bool, str | None]: Кортеж из двух элементов:
            - bool: True, если скачивание успешно или файл уже существует, False в случае ошибки.
            - str | None: Полный путь к файлу (как он должен называться на диске),
                          если скачивание успешно или файл уже существует, None в случае ошибки.
                          Важно: возвращает путь даже если файл уже существовал.
    """
    filepath = None  # Инициализируем на случай раннего выхода
    try:
        # Убедимся, что папка для загрузки существует
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Создана папка для загрузки: {folder}")

        # Формируем имя файла
        parsed_url = urlparse(pdf_url)
        pdf_filename_from_url = os.path.basename(parsed_url.path)

        # Отдаем приоритет имени файла из URL, если оно валидно и заканчивается на .pdf
        if pdf_filename_from_url and pdf_filename_from_url.lower().endswith(".pdf"):
            filename_base = sanitize_filename(pdf_filename_from_url)
        else:
            # В противном случае используем название игры + .pdf
            filename_base = sanitize_filename(
                game_title
            )  # sanitize_filename добавит .pdf если нужно

        # Составляем полный путь к файлу
        filepath = os.path.join(folder, filename_base)

        # Проверяем, существует ли файл уже
        if os.path.exists(filepath):
            print(f"Пропускаем скачивание: '{filename_base}' уже существует.")
            # Возвращаем True и путь к существующему файлу
            return True, filepath

        # Если файла нет, пытаемся скачать
        print(f"Пытаемся скачать PDF для '{game_title}' из: {pdf_url}")
        headers = {  # делаеем запрос к серверу очеловеченным
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": BASE_URL,  # Добавляем реферер
        }
        response = requests.get(
            pdf_url, stream=True, headers=headers, timeout=60, allow_redirects=True
        )
        response.raise_for_status()

        final_url = response.url
        content_type = response.headers.get("content-type", "").lower()
        is_pdf_content = "application/pdf" in content_type
        is_pdf_url = final_url.lower().endswith(".pdf")

        if not (is_pdf_url or is_pdf_content):
            print(
                f"Пропускаем: Конечный URL '{final_url}' не похож на PDF для '{game_title}'. Content-Type: {content_type}"
            )
            # Важно: возвращаем False и путь, который был бы использован, если бы скачивание началось
            return False, filepath

        # Скачиваем файл
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Успешно скачан: '{filename_base}'")
        # Возвращаем True и путь к скачанному файлу
        return True, filepath

    except requests.exceptions.Timeout:
        print(f"Ошибка таймаута при скачивании PDF для '{game_title}' из {pdf_url}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка скачивания PDF для '{game_title}' из {pdf_url}: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка во время скачивания для '{game_title}': {e}")

    # В случае любой ошибки возвращаем False и путь, если он был определен, иначе None
    return False, filepath


# --- Основной скрипт ---

if __name__ == "__main__":
    print("Запуск скрипта скачивания PDF для EZBoardGames...")
    print(f"Файлы будут сохранены в: {DOWNLOAD_FOLDER}")
    print(f"Метаданные будут сохранены в: {METADATA_FILENAME}")

    # Создаем папку для загрузок, если она не существует
    if not os.path.exists(DOWNLOAD_FOLDER):
        try:
            os.makedirs(DOWNLOAD_FOLDER)
            print(f"Создана папка для загрузки: {DOWNLOAD_FOLDER}")
        except OSError as e:
            print(f"Ошибка создания папки '{DOWNLOAD_FOLDER}': {e}")
            exit()

    total_pdfs_found_links = 0
    total_pdfs_processed_success = 0  # Счетчик успешно скачанных ИЛИ уже существующих
    total_games_processed = 0
    processed_game_urls = set()
    # Список для хранения словарей с метаданными
    rules_metadata = []

    # Итерируемся по страницам пагинации
    for page_num in range(START_PAGE, END_PAGE + 1):
        if page_num == 1:
            list_page_url = f"{BASE_URL}/games/"
        else:
            list_page_url = f"{BASE_URL}/games/{page_num}/"

        print(f"\n--- Обработка страницы списка {page_num}: {list_page_url} ---")

        try:
            time.sleep(REQUEST_DELAY)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            list_response = requests.get(list_page_url, timeout=30, headers=headers)
            list_response.raise_for_status()
            list_soup = BeautifulSoup(list_response.content, "html.parser")

            game_articles = list_soup.find_all("article", class_="elementor-post")
            game_links_on_page = []
            for article in game_articles:
                title_tag = article.find("h3", class_="elementor-post__title")
                if title_tag:
                    link_tag = title_tag.find("a", href=True)
                    if link_tag:
                        game_page_url = urljoin(BASE_URL, link_tag["href"])
                        if game_page_url not in processed_game_urls:
                            game_links_on_page.append(game_page_url)
                            processed_game_urls.add(game_page_url)

            if not game_links_on_page:
                print(f"Новых ссылок на игры на странице {page_num} не найдено.")
                continue

            print(
                f"Найдено {len(game_links_on_page)} новых ссылок на игры на странице {page_num}."
            )

            # Посещаем каждую страницу игры
            for game_url in game_links_on_page:
                total_games_processed += 1
                print(f"\nОбработка страницы игры: {game_url}")
                time.sleep(REQUEST_DELAY)

                current_game_title = "Unknown Game"
                pdf_url_found = None  # Храним найденный URL PDF

                try:
                    game_response = requests.get(game_url, timeout=30, headers=headers)
                    if (
                        game_response.url == BASE_URL
                        or game_response.status_code >= 400
                    ):
                        print(
                            f"Пропускаем: Страница игры {game_url} перенаправила или вернула ошибку {game_response.status_code}"
                        )
                        continue
                    game_response.raise_for_status()
                    game_soup = BeautifulSoup(game_response.content, "html.parser")

                    # Извлекаем название игры
                    title_tag = game_soup.find(
                        "h1", class_="elementor-heading-title"
                    ) or game_soup.find("h1")
                    if title_tag:
                        current_game_title = title_tag.text.strip()

                    print(f"Название игры: {current_game_title}")

                    # Ищем ссылку "View Game Rules"
                    rule_link_tag = None
                    button_widget = game_soup.find(
                        "div", class_="elementor-element-d549305"
                    )
                    if button_widget:
                        rule_link_tag = button_widget.find(
                            "a", class_="elementor-button", href=True
                        )
                    # ... (остальные запасные варианты поиска ссылки)
                    if not rule_link_tag:
                        rule_link_tag = game_soup.find(
                            "a",
                            class_="elementor-button",
                            href=True,
                            string=lambda text: text
                            and "view game rules" in text.strip().lower(),
                        )
                    if not rule_link_tag:
                        possible_links = game_soup.find_all(
                            "a", class_="elementor-button", href=True
                        )
                        for link in possible_links:
                            button_text_span = link.find(
                                "span", class_="elementor-button-text"
                            )
                            if (
                                button_text_span
                                and "view game rules"
                                in button_text_span.text.strip().lower()
                            ):
                                rule_link_tag = link
                                break

                    if rule_link_tag:
                        pdf_url_relative = rule_link_tag["href"]
                        pdf_url_found = urljoin(
                            game_url, pdf_url_relative
                        )  # Сохраняем URL

                        if pdf_url_found.lower().endswith(".pdf"):
                            total_pdfs_found_links += 1
                            print(f"Найдена ссылка на PDF: {pdf_url_found}")

                            # Пытаемся скачать файл и получаем результат и путь к файлу
                            success, target_filepath = download_pdf(
                                pdf_url_found, current_game_title, DOWNLOAD_FOLDER
                            )

                            # Если скачивание успешно ИЛИ файл уже существует (success=True)
                            # И путь к файлу был определен (target_filepath не None)
                            if success and target_filepath:
                                total_pdfs_processed_success += 1
                                # Извлекаем только имя файла из полного пути
                                actual_filename = os.path.basename(target_filepath)

                                # Создаем словарь с метаданными
                                metadata_entry = {
                                    "title": current_game_title,
                                    "filename": actual_filename,  # Имя файла на диске
                                    "url": pdf_url_found,  # URL, откуда скачивали
                                }
                                # Добавляем словарь в список
                                rules_metadata.append(metadata_entry)
                                print(
                                    f"Метаданные для '{current_game_title}' добавлены."
                                )

                        else:
                            print(
                                f"Пропускаем: Ссылка найдена для '{current_game_title}', но URL не заканчивается на .pdf ({pdf_url_found})"
                            )
                    else:
                        print(
                            f"Не удалось найти ссылку 'View Game Rules' (PDF) для '{current_game_title}'."
                        )

                except requests.exceptions.Timeout:
                    print(f"Ошибка таймаута при загрузке страницы игры {game_url}")
                except requests.exceptions.RequestException as e:
                    print(
                        f"Ошибка при загрузке или обработке страницы игры {game_url}: {e}"
                    )
                except Exception as e:
                    print(
                        f"Неожиданная ошибка при обработке страницы игры {game_url} ({current_game_title}): {e}"
                    )

        except requests.exceptions.Timeout:
            print(f"Ошибка таймаута при загрузке страницы списка {list_page_url}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке страницы списка {list_page_url}: {e}")
            if e.response is not None:
                print(f"Статус код: {e.response.status_code}")
        except Exception as e:
            print(
                f"Неожиданная ошибка при обработке страницы списка {list_page_url}: {e}"
            )

    # --- Запись JSON-файла с метаданными ---
    print("\n--- Запись JSON метаданных ---")
    try:
        # сортируем список словарей по названию игры для удобства
        rules_metadata.sort(key=lambda x: x.get("title", "").lower())

        # Открываем файл для записи JSON
        with open(METADATA_FILENAME, "w", encoding="utf-8") as f:
            # Записываем список словарей в файл JSON
            # indent=4 делает файл читаемым (с отступами)
            # ensure_ascii=False позволяет сохранять не-ASCII символы (например, кириллицу) как есть
            json.dump(rules_metadata, f, ensure_ascii=False, indent=4)

        print(
            f"Метаданные для {len(rules_metadata)} игр сохранены в: {METADATA_FILENAME}"
        )
    except IOError as e:
        print(f"Ошибка записи JSON файла '{METADATA_FILENAME}': {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при записи JSON файла: {e}")

    # --- Итоговая информация ---
    print(f"\n--- Скрипт завершен ---")
    print(f"Всего обработано страниц списка: {END_PAGE - START_PAGE + 1}")
    print(f"Всего обработано уникальных страниц игр: {total_games_processed}")
    print(f"Всего найдено потенциальных ссылок на PDF: {total_pdfs_found_links}")
    # Используем len(rules_metadata) как самый точный счетчик успешных записей
    print(
        f"Всего игр с успешно обработанными правилами (скачаны или найдены): {len(rules_metadata)}"
    )
    print(f"Файлы PDF сохранены в папку: '{DOWNLOAD_FOLDER}'")
    print(f"Метаданные игр сохранены в файл: '{METADATA_FILENAME}'")
