**Запуск beat сервиса**

	python manage.py celery -A telegram_shop_bot beat -l info -S djcelery.schedulers.DatabaseScheduler --settings=telegram_shop_bot.settings.prod
	
**Запуск flower (для мониторинга)**

	python manage.py celery flower -A telegram_shop_bot --address=127.0.0.1 --port=5555
	
**Запуск uwsgi сервера**
```
uwsgi --ini ./shop_bot.uwsgi.ini  --socket :8002
```
	
**Запуск воркеров**

	python manage.py celery -A telegram_shop_bot worker -l info --events -c 1 --settings=telegram_shop_bot.settings.prod
	
	
**Регламент первой установки**
1) обновить исходники
2) установить пакеты через pip
3) выполнить миграции
4) собрать статику
5) создать таблицу кэша (python manage.py createcachetable)
6) перечитать конфиги supervisor
7) стартануть web-сервер через supervisor


**Регламент обновления (полуавтоматическое)**
1) запустить fabric
```
fab -H do_webrunner deploy:tag_name="release_4.7_2017-04-06"
```
   
где "release_4.7_2017-04-06" - название тега, который надо развернуть

2) ввести sudo пароль


**Регламент обновления (ручное)**
1) обновить исходники
2) установить пакеты через pip   # pip install -r ./requirements.txt
3) сделать бекап БД              # pg_dump -h localhost -O shop_bot_prod -f /home/webrunner/backups/$(date +"%Y-%m-%d_%H-%M")
4) выполнить миграции            # python manage.py migrate
5) обновить конфиг supervisor                          # sudo supervisorctl reread && sudo supervisorctl update
6) перезагрузить web-сервер через supervisor           # sudo supervisorctl restart shop_bot:



**ключевые части кода для работы**

more_command = create_uri(TextCommandEnum.GET_CATALOG, catalog_id=catalog_id, offset=new_offset)

query_dict = get_query_dict(call_data)
catalog_id_str = query_dict.get('catalog_id')
