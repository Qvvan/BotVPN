from environs import Env

env = Env()
env.read_env()

DSN = env.str("DSN")

CRYPTO_KEY = env.str("CRYPTO_KEY")

ADMIN_IDS = [int(admin) for admin in env.list('ADMIN_IDS')]

BOT_TOKEN = env.str("BOT_TOKEN")

ERROR_GROUP_ID = env.int("ERROR_GROUP_ID")
INFO_GROUP_ID = env.int("INFO_GROUP_ID")

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)

OUTLINE_USERS_GATEWAY = env.str('OUTLINE_USERS_GATEWAY')
OUTLINE_SALT = env.str('OUTLINE_SALT')
