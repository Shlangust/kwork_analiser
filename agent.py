from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from config import agent_key
from excel import add_col

main = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=None,
    api_key=agent_key,
)
fallback1 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=None,
    api_key=agent_key,
)
fallback2 = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7,
    max_tokens=None,
    api_key=agent_key,
)

agent = main.with_fallbacks([fallback1, fallback2])
stack = """
УМЕЮ (основное):
- Python: парсинг (BeautifulSoup, Selenium, playwright), автоматизация, анализ данных (Pandas, NumPy)
- Telegram-боты: Aiogram, Pyrogram, Telebot
- Веб-сервисы: Flask, REST API
- БД: PostgreSQL, MySQL, SQLite + SQLAlchemy
- Инфраструктура: Docker, Linux, Nginx, деплой на VPS (Beget), Git
- Фронтенд (базовый): HTML/CSS/JavaScript, вёрстка по макетам Figma
- Доп: Asyncio, openpyxl, Tesseract (OCR), Unittest, Requests, langchain

ИЗУЧАЮ (могу взять несложное):
- Go (в процессе)

НЕ БЕРУСЬ:
- Мобильная разработка (iOS/Android)
- 1С, Bitrix, AmoCRM и подобное
- Чистый фронтенд / React / Vue (без Python-бэкенда)
- C++ / C# проекты (базовые знания, не коммерческий опыт)
- UI/UX дизайн с нуля (вёрстка по готовым макетам — да, дизайн сам — нет)
"""



stack_prompt = ChatPromptTemplate.from_messages([
    ("system", """Ты — технический фильтр для фрилансера.
Твоя задача: понять, сможет ли фрилансер выполнить этот заказ.

Стек фрилансера:
{stack}

Правила оценки:
- Оценивай что НУЖНО СДЕЛАТЬ, а не как это описано заказчиком
- Игнорируй пожелания заказчика про ИИ/без ИИ — это не про стек
- Если задача — парсинг, скрипт, автоматизация на Python → fits: true
- Если задача требует фронтенда, смотри есть ли Python-бэкенд в задаче
  Если фронтенд упомянут как часть задачи, но суть — бэкенд/скрипт → fits: true
- fits: false только если задача ЯВНО вне стека (1С, iOS, чистый React и т.д.)
- Если ТЗ размытое и невозможно оценить → unclear: true, fits: false
- reason — одна короткая фраза о сути задачи, не о причине отказа

Верни ТОЛЬКО валидный JSON, без пояснений."""),
("human", """Скрипт на n8n, либо любой другой ЯП
Нужно написать шаблон на n8n (возможен другой язык программирование - главное чтобы удобно было пользоваться):
1) в Chatgpt или Gemini делать: есть авторы которые хорошо пишут посты, нужно брать посты не старше 2-3 дней - делать классный рерайт, чтобы они выглядели ещё лучше и интереснее и делать цепляющий заголовок. Должно получиться: заголовок + сам пост
2) подключаться к capcut, либо к edits и менять подложку (рандомно из загруженных видео файлов) и вставлять полученный заголовок
3) загружать в отдельную папку на Яндекс.Диск - видео + текст поста (получается два файла).
Если сложно сделать первый пункт сложно, то есть уже готовый список постов которые хорошо заходят - надо засовывать их в claude ai прогонять через несколько постов и переходить ко 2 и 3 пункту."""),
    ("ai", """{{
  "fits": true,
  "unclear": false,
  "reason": "Автоматизация: рерайт постов через ИИ + замена подложки в видео + загрузка на Яндекс.Диск"
}}"""),

    ("human", """Интеграции битрикса
Нам нужен специалист на удаленке для работы в нашем битрикс24. Настройка генерации документов, настройка интеграций и тп"""),
    ("ai", """{{
  "fits": false,
  "unclear": false,
  "reason": "Настройка и интеграции Битрикс24"
}}"""),

    ("human", """Ограниченное тестирование Android на 12 устройствах
Ограниченное тестирование Android приложения на множестве аккаунтов и устройств под требования Google в течение 14 дней
Необходимо иметь около 12 аккаунтов и устройств – разная диагональ, разные версии Android от 10 до 16.
Необходимо
- установить приложение на 12 устройствах и проверить, что приложение запускается на всех.
- открыть его хотя бы несколько раз за 14 дней;
- не удалять приложение;
- не выходить из программы тестирования;
- иногда выполнять основные действия внутри приложения."""),
    ("ai", """{{
  "fits": false,
  "unclear": false,
  "reason": "Тестирование Android-приложения на реальных устройствах"
}}"""),
    ("human", "Название: {name}\n\nТЗ: {task}")
])

stack_chain = stack_prompt | agent | JsonOutputParser()

def stack_chek(parse_data):
    answer = stack_chain.invoke(
        {
            "stack": stack,
            "name": parse_data["title"],
            "task": parse_data["task"]
        }
    )
    return {"fits":answer.get("fits"), "unclear":answer.get("unclear"), "reason":answer.get("reason")}


response_prompt = ChatPromptTemplate.from_messages([
    ("system", """Ты — опытный фрилансер, пишешь реальный отклик на Kwork.

Стиль:
- Живой разговорный русский, как в мессенджере
- Сразу по делу, без вступлений
- Обращение только на "Вы"
- Максимум 1 короткий абзац про опыт (если вообще нужен)
- Дальше сразу уточняющие вопросы
- Без смайликов вообще
- Без слов "Итак", "Понял задачу", "Сделаю следующее", "Готов взяться" и подобных шаблонов

Структура хорошего отклика:
1. Очень коротко и по-человечески — что именно сделаешь (1-2 предложения максимум)
2. Если нужно — одна короткая фраза про релевантный опыт
3. Сразу вопросы, которые реально нужны, чтобы начать"""),
("human", "Название: {title}\n\nТЗ: {task}\n\nТЗ размытое: {unclear}")])

response_chain = response_prompt | agent | StrOutputParser()

def make_answer(data):
    answer = response_chain.invoke(
        {
            "title":data["title"],
            "task":data["task"],
            "unclear":data["unclear"]})
    return answer