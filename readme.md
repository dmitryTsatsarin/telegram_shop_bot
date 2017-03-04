**Запуск beat сервиса**

	python manage.py celery -A telegram_shop_bot beat -l info -S djcelery.schedulers.DatabaseScheduler --settings=telegram_shop_bot.settings.prod
	
**Запуск flower (для мониторинга)**

	python manage.py celery flower -A telegram_shop_bot --address=127.0.0.1 --port=5555
	
**Запуск uwsgi сервера**
    uwsgi --ini ./shop_bot.uwsgi.ini  --socket :8002
	
	
**Запуск воркеров**

	python manage.py celery -A telegram_shop_bot worker -l info --events -c 1 --settings=telegram_shop_bot.settings.prod
	
	
**Регламент обновления**
1) обновить исходники
2) установить пакеты через pip
3) выполнить миграции
4) перезагрузить web-сервер через supervisor