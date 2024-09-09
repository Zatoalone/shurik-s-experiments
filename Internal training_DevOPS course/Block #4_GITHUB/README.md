# Бот
Для запуска бота необходимо:
1. На машине от куда будем запускать [playbook_tg_bot.yml](playbook_tg_bot.yml) установить `ansible`;
2. Указать в `ansible.cfg` путь до [inventory](inventory);
3. Подготовить 3 VM описанные в [inventory](inventory);
4. Внести изменения в  [db_configs](db_configs), [schema.sql](schema.sql) и [playbook_tg_bot.yml](playbook_tg_bot.yml) при использовании своих паролей и ip адресов;
5. В [template_env](template_env) указать параметры для подключения к хосту мониторинга, TG и PG;
6. Выполнить `ansible-playbook playbook_tg_bot.yml`
