# -*- coding: utf-8 -*-
__author__ = 'forward'
import time

from fabric.api import run, env
from fabric.context_managers import cd, prefix
from fabric.operations import local, get, sudo

env.use_ssh_config = True


def host_type():
    local('uname -s')


def create_backup_filename():
    backup_filename = run('echo $(date +"%Y-%m-%d_%H-%M")')
    return backup_filename


def make_backup(backup_filename):
    backup_path = '/home/webrunner/backups/%s' % backup_filename
    run('pg_dump -h localhost -O shop_bot_prod -f %s' % backup_path)
    return backup_path


def pull_backup(backup_filename, remote_full_backup_path):
    get(remote_path=remote_full_backup_path, local_path="/home/forward/Dropbox/backup/%s" % backup_filename)


def install_requirements():
    run('pip install -r ./requirements.txt')


def git_fetch_and_checkout(tag_name):
    run('git fetch --all')
    run('git checkout %s' % tag_name)


def collect_static():
    run('python manage.py collectstatic --noinput')


def migrate():
    run('python manage.py migrate')


def update_supervisor():
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def restart_everything_in_shop_bot():
    sudo('supervisorctl restart shop_bot:')


def check_final_status():
    time.sleep(3)  # делаем паузу в несколько секунд
    result = sudo('supervisorctl status shop_bot:')
    if 'STOPPED' in result:
        raise Exception('Attention!!! Some process is STOPPED!!!!!')


def deploy(tag_name=None):
    if not tag_name:
        raise Exception('TSD. Need a tag name')

    with cd("/home/webrunner/telegram_shop_bot/src/telegram_shop_bot"):
        # 1) обновить исходники
        git_fetch_and_checkout(tag_name)
        with prefix('source /home/webrunner/venvs/env_shop_bot/bin/activate'):
            # 2) установить пакеты через pip
            install_requirements()

            collect_static()

            # 3) сделать бекап БД и сохранить на локальную тачку
            backup_filename = create_backup_filename()
            remote_full_backup_path = make_backup(backup_filename)
            pull_backup(backup_filename, remote_full_backup_path)

            # 4) выполнить миграции
            migrate()

            # 5) обновить конфиг supervisor
            update_supervisor()

            # 6) перезагрузить web-сервер через supervisor
            restart_everything_in_shop_bot()

            # -) проверка финального статуса
            check_final_status()
