from environs import Env

env = Env()
env.read_env()

DSN = env.str("DSN")

CRYPTO_KEY = env.str("CRYPTO_KEY")

ADMIN_IDS = [int(admin) for admin in env.list('ADMIN_IDS')]

BOT_TOKEN = env.str("BOT_TOKEN")

ERROR_GROUP_ID = env.int("ERROR_GROUP_ID")
INFO_GROUP_ID = env.int("INFO_GROUP_ID")