
from django.core.management.base import BaseCommand

from shop_bot_app.logic import bot




class Command(BaseCommand):
    # help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        bot.polling(none_stop=True)
