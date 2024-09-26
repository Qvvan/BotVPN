from environs import Env

env = Env()
env.read_env()

DSN = env.str("DSN")

CRYPTO_KEY = env.str("CRYPTO_KEY")

ADMIN_IDS = [int(admin) for admin in env.list('ADMIN_IDS')]

BOT_TOKEN = env.str("BOT_TOKEN")