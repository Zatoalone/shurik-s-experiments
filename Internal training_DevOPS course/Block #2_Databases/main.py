import os
from dotenv import load_dotenv
import logging
import re
import paramiko
import psycopg2
from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()
TOKEN = os.getenv('TOKEN')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
ALLOWED_IDS = []
for aid in os.getenv('ALLOWED_ID').split(' '):
    ALLOWED_IDS.append(int(aid))
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_DB = os.getenv('PG_DB')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def check_user(user_id: int) -> bool:
    """
    Функция проверки пользователя

    Если id пользователь есть в списке ALLOWED_IDS, бот будет взаимодействовать с пользователем.
    :param user_id: Id пользователя
    :return: Вернет True если проверка пройдена иначе False
    """
    if user_id in ALLOWED_IDS:
        return True
    else:
        return False


def remote_exec(host: str, port: str, username: str, password: str, command: str) -> str:
    """
    Функция установки подключения по ssh к удаленному хосту и выполнения переданной команды.
    :param host: Ip удаленного хоста. Например, 127.0.0.1.
    :param port: Порт подключения по по протоколу ssh. Например, 22.
    :param username: Логин пользователя.
    :param password: Пароль пользователя.
    :param command: Комманда для выполнения. Например, cat /etc/*-release.
    :return: Возвращается результат отработанной команды.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port, look_for_keys=False,
                   allow_agent=False,)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data.decode('utf-8')).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def pg_exec(pg_user: str, pg_password: str, pg_host: str, pg_port: str, pg_db: str, command: str) -> list:
    connection = None
    try:
        connection = psycopg2.connect(user=pg_user, password=pg_password, host=pg_host, port=pg_port, database=pg_db)
        cursor = connection.cursor()
        cursor.execute(command)
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
        return data
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


def start(update: Update, context):
    """
    Команда приветствия

    Бот поздоровается с пользователем.
    """
    user = update.effective_user
    if check_user(user.id):
        update.message.reply_text(f'Привет {user.full_name}!')


def help_command(update: Update, context):
    """
    Команда помощи

    Бот вернет список поддерживаемых команд с их описанием.
    """
    user = update.effective_user
    if check_user(user.id):
        help = ("Что умеет бот:\n"
                "1. Искать mail в тексте: /find_email\n"
                "2. Искать телефонные номера в тексте: /find_phone_number\n"
                "3. Проверять пароль на сложность: /verify_password\n"
                "4. Показать информацию о релизе ОС: /get_release\n"
                "5. Показать информацию о архитектуре: /get_uname\n"
                "6. Показать время работы ОС: /get_uptime\n"
                "7. Показать состояние Файловой системы: /get_df\n"
                "8. Показать состояние оперативной памяти: /get_free\n"
                "9. Показать производительность системы: /get_mpstat\n"
                "10. Показать работающих в системе пользователей: /get_w\n"
                "11. Показать последние 10 входов в систему: /get_auths\n"
                "12. Показать последние 5 критических события: /get_critical\n"
                "13. Показать запущенные процессы: /get_ps\n"
                "14. Показать используемые порты: /get_ss\n"
                "15. Показать установленные пакеты: /get_apt_list\n"
                "16. Показать запущенные сервисы: /get_services\n"
                "17. Показать статус репликации PG: /get_repl_logs\n"
                "18. Показать содержимое таблицы emails: /get_emails")
        update.message.reply_text(help)


def find_email_command(update: Update, context):
    """
    Комманда поиска email'ов в тексте

    Бот запросит ввести текст для поиска email'ов.
    """
    user = update.effective_user
    if check_user(user.id):
        update.message.reply_text('Введите текст для поиска email: ')
        return 'find_email'


def find_phone_numbers_command(update: Update, context):
    """
    Комманда поиска телефонных номеров в тексте

    Бот запросит ввести текст для поиска телефонных номеров.
    """
    user = update.effective_user
    if check_user(user.id):
        update.message.reply_text('Введите текст для поиска телефонных номеров: ')
        return 'find_phone_number'


def verify_password_command(update: Update, context):
    """
    Комманда проверки сложности пароля

    Бот запросит ввести пароль для проверки его сложности.
    """
    user = update.effective_user
    if check_user(user.id):
        update.message.reply_text('Введите пароль для проверки: ')
        return 'verify_password'


def get_apt_list_command(update: Update, context):
    """
    Комманда поиска установленных пакетов в ОС

    Бот запросит ввести название искомого пакета или написать all для вывода всех установленных пакетов.
    """
    user = update.effective_user
    if check_user(user.id):
        update.message.reply_text('Информации об установленных пакетах. \n Введите название пакета или \"all '
                                  '(вернетсписок всех установленых пакетов) \" ')
        return 'get_apt_list'


def find_email(update: Update, context):
    """
    Обработчик даных запрошеных через find_email_command
    """
    user = update.effective_user
    if check_user(user.id):
        user_input = update.message.text
        email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        email_number_list = email_regex.findall(user_input)
        if not email_number_list:
            update.message.reply_text('Email не найдены')
            return ConversationHandler.END
        emails = ''
        for i in range(len(email_number_list)):
            emails += f'{i + 1}. {email_number_list[i]}\n'
        update.message.reply_text(emails)
        return ConversationHandler.END


def find_phone_numbers(update: Update, context):
    """
    Обработчик даных запрошеных через find_phone_numbers_command
    """
    user = update.effective_user
    if check_user(user.id):
        user_input = update.message.text
        phone_num_regex = re.compile(r'\+?[78]\s?[-\(]?\d{3}\)?\s?-?\d{3}\s?-?\d{2}\s?-?\d{2}')
        phone_number_list = phone_num_regex.findall(user_input)
        if not phone_number_list:
            update.message.reply_text('Телефонные номера не найдены')
            return ConversationHandler.END
        phone_numbers = ''
        for i in range(len(phone_number_list)):
            phone_numbers += f'{i + 1}. {phone_number_list[i]}\n'
        update.message.reply_text(phone_numbers)
        return ConversationHandler.END


def verify_password(update: Update, context):
    """
    Обработчик даных запрошеных через verify_password_command
    """
    user = update.effective_user
    if check_user(user.id):
        user_input = update.message.text
        password_regex = re.compile(r'(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}')
        password = password_regex.search(user_input)
        if password:
            update.message.reply_text('Пароль сложный')
        else:
            update.message.reply_text('Пароль слабый')
        return ConversationHandler.END


def get_release(update: Update, context):
    """
    Комманда вывода информации о релизе
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'cat /etc/*-release')
        update.message.reply_text("Информация о релизе")
        update.message.reply_text(data)


def get_uname(update: Update, context):
    """
    Команда вывода информации об архитектуры процессора, имени хоста системы и версии ядра
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'uname -i && uname -n && uname -v')
        inp_data = data.split("\n")
        out_data = f"Архитектура: {inp_data[0]}\nИмя хоста: {inp_data[1]}\nВерсия ядра: {inp_data[2]}"
        update.message.reply_text("Информация о архитектуры процессора, имени хоста системы и версии ядра")
        update.message.reply_text(out_data)


def get_uptime(update: Update, context):
    """
    Команда вывода информации о времени работы
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'uptime -p')
        update.message.reply_text("Время работы хоста")
        update.message.reply_text(data)


def get_df(update: Update, context):
    """
    Команда вывода информации о состоянии файловой системы
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'df -Th')
        out = ""
        i = 0
        for line in data.split("\n")[1:-1]:
            tmp_line = re.sub(" +", " ", line).split(" ")
            i += 1
            out += (f"{i}. *ФС:* `{tmp_line[0]}`  *Монтировано:* `{tmp_line[6]}`  *Тип:* `{tmp_line[1]}`  "
                    f"*Утилизация:* `{tmp_line[3]}/{tmp_line[2]}` \n")
        update.message.reply_text("Файловая система")
        update.message.reply_text(text=out, parse_mode='Markdown')


def get_free(update: Update, context):
    """
    Команда вывода информации о состоянии оперативной памяти
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'free -h')
        out = ""
        i = 0
        for line in data.split("\n")[1:-1]:
            i += 1
            tmp_line = re.sub(" +", " ", line).split(" ")
            out += (f"{i}. *{tmp_line[0]}*  *Всего:* `{tmp_line[1]}`  *Использовано:* `{tmp_line[2]}`  "
                    f"*Свободно:* `{tmp_line[3]}` *Разделяемая память:* "
                    f"`{tmp_line[4] if tmp_line.__len__() > 4 else None}` *Кэш:* "
                    f"`{tmp_line[5] if tmp_line.__len__() > 4 else None}` *Доступно:* "
                    f"`{tmp_line[6] if tmp_line.__len__() > 4 else None}`\n")
        update.message.reply_text("Состояние памяти")
        update.message.reply_text(text=out, parse_mode='Markdown')


def get_mpstat(update: Update, context):
    """
    Команда вывода информации о производительности системы
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'mpstat')
        out = ""
        i = 0
        for line in data.split("\n"):
            if line.strip():
                i += 1
                tmp_line = re.sub(" +", " ", line).split(" ")
                if i == 1:
                    out += (
                        f"{i}. `{tmp_line[0]}` `{tmp_line[1]}` `{tmp_line[2]}` `{tmp_line[3]}` `{tmp_line[4]}` "
                        f"`{tmp_line[5]}` \n")
                if i == 3:
                    out += (f"{i-1}. *CPU:* `{tmp_line[1]}` *%usr*: `{tmp_line[2]}` *%nice:* `{tmp_line[3]}` "
                            f"*%sys:* `{tmp_line[4]}` *%iowait:* `{tmp_line[5]}` *%irq:* `{tmp_line[6]}` "
                            f"*%soft:* `{tmp_line[7]}` *%steal:* `{tmp_line[8]}` *%guest:* `{tmp_line[9]}` "
                            f"*%gnice:* `{tmp_line[10]}` *%idle:*`{tmp_line[11]}`\n")
        update.message.reply_text("Производительность системы")
        update.message.reply_text(text=out, parse_mode='Markdown')


def get_w(update: Update, context):
    """
    Команда вывода информации о работающих в данной системе пользователях
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'who')
        out = ""
        i = 0
        for line in data.split("\n"):
            if line.strip():
                i += 1
                tmp_line = re.sub(" +", " ", line).split(" ")
                print(tmp_line)
                out += (f"{i}. *Кто:* `{tmp_line[0]}` *Как:* `{tmp_line[1]}` *Когда:* `{tmp_line[2]} {tmp_line[3]}` "
                        f"*Откуда:* `{tmp_line[4] if tmp_line.__len__() > 4 else None}`\n")
        update.message.reply_text("Работающие пользователи в системе")
        update.message.reply_text(text=out, parse_mode='Markdown')


def get_auths(update: Update, context):
    """
    Команда вывода информации о последних 10 входах в систему
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'last -n 30 -f /var/log/wtmp')
        out = ""
        i = 0
        for line in data.split("\n")[:-2]:
            if line.strip():
                if "reboot" not in line:
                    i += 1
                    if i > 10:
                        break
                    tmp_line = re.sub(" +", " ", line)
                    out += f"{i}. {tmp_line} \n"
        update.message.reply_text("Последние 10 входов в систему")
        update.message.reply_text(text=out)


def get_critical(update: Update, context):
    """
    Команда вывода информации о последних 5 критических событиях.
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'tail -n 6 /var/log/crit.log')
        out = ""
        i = 0
        for line in data.split("\n")[:-1]:
            i += 1
            tmp_line = re.sub(" +", " ", line)
            out += f"{i}. {tmp_line} \n"
        update.message.reply_text("Последние критические события")
        update.message.reply_text(text=out)


def get_ps(update: Update, context):
    """
    Команда вывода информации о запущенных процессах
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'ps')
        update.message.reply_text("Запущенные процессы")
        if len(data) > 4096:
            for x in range(0, len(data), 4096):
                update.message.reply_text(text=data[x:x + 4096])
        else:
            update.message.reply_text(text=data)


def get_ss(update: Update, context):
    """
    Команда вывода информации об используемых портах
    """
    user = update.effective_user
    if check_user(user.id):
        chat_id = update.effective_chat.id
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'ss')
        with open("SS.txt", "w") as file:
            file.write(data)
        doc_file = open("SS.txt", "rb")
        update.message.reply_text("Используемые порты")
        update.message.bot.send_document(chat_id, doc_file)


def get_apt_list(update: Update, context):
    """
    Обработчик даных запрошеных через get_apt_list_command
    """
    user_input = update.message.text
    chat_id = update.effective_chat.id
    if user_input == "all":
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'apt list --installed')
        message = "Все пакеты:"
    else:
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, f'apt list --installed | grep {user_input}')
        message = f"Пакет {user_input}:"
    with open("apt.txt", "w") as file:
        file.write(data)
    doc_file = open("apt.txt", "rb")
    update.message.reply_text(message)
    update.message.bot.send_document(chat_id, doc_file)
    return ConversationHandler.END


def get_services(update: Update, context):
    """
    Команда вывода информации о запущенных сервисах
    """
    user = update.effective_user
    if check_user(user.id):
        chat_id = update.effective_chat.id
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'systemctl list-units --type=service')
        with open("services.txt", "w") as file:
            file.write(data)
        doc_file = open("services.txt", "rb")
        update.message.reply_text("Запущенные сервисы")
        update.message.bot.send_document(chat_id, doc_file)


def get_repl_logs(update: Update, context):
    """
    Команда вывода логов о репликации из /var/log/postgresql/
    """
    user = update.effective_user
    if check_user(user.id):
        data = remote_exec(HOST, PORT, USERNAME, PASSWORD, 'cat /var/log/postgresql/postgresql-15-main.log | grep repl_user | tail -n 3')
        print(data)
        out = ""
        i = 0
        for line in data.split("\n"):
            i += 1
            tmp_line = re.sub(" +", " ", line)
            out += f"{i}. {tmp_line} \n"
        update.message.reply_text("Последние логи о репликации")
        update.message.reply_text(text=out)


def get_emails(update: Update, context):
    """
    Команда вывода информации из таблицы emails
    """
    user = update.effective_user
    if check_user(user.id):
        data = pg_exec(PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB, "SELECT * FROM emails;")
        out = ""
        i = 0
        for line in data:
            i += 1
            out += f"{i}. ID: {line[0]}, Email: {line[1]}\n"
        print(len(out))
        update.message.reply_text("Содержимое таблицы emails")
        if len(out) > 4096:
            for x in range(0, len(out), 4096):
                update.message.reply_text(text=out[x:x + 4096])
        else:
            update.message.reply_text(text=out)


def main():
    updater = Updater(TOKEN, use_context=True)
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
    # Обработчики диалогов
    conv_handler_find_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numbers_command)],
        states={'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_numbers)], },
        fallbacks=[]
    )
    conv_handler_find_emails = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_command)],
        states={'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)], },
        fallbacks=[]
    )
    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)], },
        fallbacks=[]
    )
    conv_handler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)], },
        fallbacks=[]
    )

    # Регистрация обработчиков команд

    # Однострочники
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    # Диалоговые
    dp.add_handler(conv_handler_find_phone_numbers)
    dp.add_handler(conv_handler_find_emails)
    dp.add_handler(conv_handler_verify_password)
    dp.add_handler(conv_handler_get_apt_list)

    # Запускаем бота
    updater.start_polling()
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
