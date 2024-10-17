from environs import Env

env = Env()
env.read_env()

DSN = env.str("DSN")
OUTLINE_SALT = env.str("OUTLINE_SALT")
CRYPTO_KEY = env.str("CRYPTO_KEY")
