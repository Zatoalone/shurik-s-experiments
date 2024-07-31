# Бот
Для запуска бота необходимо:
1. Установить вируальное окружение: `python3 -m venv <название виртуального окружения>` 
2. Активировать виртуальное окружение: `source /путь/до/<название виртуального окружения>/bin/activate`
3. Установить зависимости: `pip install -r requirements.txt`
4. Поготовить `.env` файл в одной директории с ботом со следующим содержанием:
    * `TOKEN = <Токен телеграм бота>`
    * `HOST = <IP удаленного хоста для подключения по ssh>`
    * `PORT = <Порт для подключения по ssh>`
    * `USER = <Login с разрешением для подключения по ssh к удаленному хосту>` 
    * `PASSWORD = <Пароль>`
    * `ALLOWED_ID = <ID или список ID (через пробел) пользователей взаимодействующих с ботом>`
    * `PG_HOST = <IP CУБД postgresql>` 
    * `PG_PORT = <Порт для подключения к postgresql>` 
    * `PG_USER = <Login для подключения к postgresql>` 
    * `PG_PASSWORD = <Пароль>` 
    * `PG_DB = <Название базы данных>`
5. На удаленном хосте должны быть установлены пакеты:
    * `apt-get install sysstat`
    * `apt-get rsyslog`
    * `apt install postgresql postgresql-contrib`
6. В конфигурационный файл `rsyslog.conf` необходимо внести следующие настройки:
    * Кастомный формат вывода `$template myFormat, "%syslogfacility-text%:%syslogpriority-text% %timegenerated% %hostname% %syslogtag%%msg:::drop-last-lf%\n”`
    * Правило отправки `*.crit /var/log/crit.log;myFormat`
7. В конфигурационном файле `postgresql.conf` необходимо внести следующие настройки:
    * `listen_addresses = <ip адрес(а) сетевого интерфейса который будет слушать postgres>`
8. В Конфигурационном файле `pg_hba.conf` необходимо внести следующие настройки:
    * `host    all             all        <ip адрес бота>/24        md5`
9. В postgresql:
    * Создать базу данных `CREATE database <Название базы данных> OWNER postgres;`
    * Создать таблицу `emails` `CREATE TABLE emails(ID SERIAL PRIMARY KEY, email VARCHAR (100) NOT NULL);`
    * Создать таблицу `phone_numbers` `CREATE TABLE phone_numbers(ID SERIAL PRIMARY KEY, number VARCHAR (100) NOT NULL);`
    * Создать пользователя `CREATE USER <login> WITH PASSWORD '<пароль>';` 
    * Выдать пользователю права на таблицы `GRANT SELECT, INSERT ON emails TO <login>;` и `GRANT SELECT, INSERT ON phone_numbers TO <login>;`
    * Выдать пользователю права на инкрементацию первичного ключа в таблицах `GRANT USAGE, UPDATE ON SEQUENCE emails_id_seq TO <login>;` и `GRANT USAGE, UPDATE ON SEQUENCE phone_number_id_seq TO <login>;`
10. Если используется репликация postgresql(master/slave):
    * На сервере `master` включаем настройки в `postgresql.conf`: `archive_mode = on`, `archive_command = 'cp %p /var/pg_data/archive/%f'`, `max_wal_senders = 10`, `wal_level = replica` и `log_replication_commands = on`
    * На сервере `master` включаем настройки в `pg_hba.conf`: `host    replication     repl_user       <ip адрес slave>/24           scram-sha-256`
    * На сервере `slave` стваим пакеты `apt install postgresql postgresql-contrib`
    * На сервере `slave` включаем настройки в `postgresql.conf`: `listen_addresses = <ip адрес(а) сетевого интерфейса который будет слушать postgres>`
    * На сервере `slave` выполняем команды: `systemctl stop postgresql`, `rm -rf /var/lib/postgresql/15/main/*`, `pg_basebackup -R -h <ip адрес master> -U repl_user -D /var/lib/postgresql/15/main -P` и `systemctl stop postgresql`
    * Репликация настроена
    
11. Запускаем бота командой: `python3 main.py`