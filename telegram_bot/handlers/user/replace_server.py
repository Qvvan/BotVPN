from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.context_manager import DatabaseContextManager
from handlers.services.get_session_cookies import get_session_cookie
from handlers.services.key_create import ShadowsocksKeyManager, VlessKeyManager
from keyboards.kb_inline import InlineKeyboards, ServerSelectCallback, \
    SubscriptionCallbackFactory
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import NameApp
from models.models import Subscriptions
from state.state import ChoiceServer

router = Router()

class ServerUnavailableError(Exception):
    """Кастомное исключение для недоступного сервера."""
    pass


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'replace_server'))
async def get_support(callback_query: CallbackQuery, state: FSMContext, callback_data: SubscriptionCallbackFactory):
    await callback_query.answer()
    subscription_id = callback_data.subscription_id
    state_data = await state.get_data()
    server_ip = state_data.get("server_ip")

    await state.update_data(
        subscription_id=subscription_id,
    )

    await callback_query.message.answer(
        text='Выбери подходящую для себя локацию',
        reply_markup=await InlineKeyboards.get_servers(server_ip),
    )
    await state.set_state(ChoiceServer.waiting_for_choice)


@router.callback_query(ServerSelectCallback.filter(), ChoiceServer.waiting_for_choice)
async def handle_server_selection(callback_query: CallbackQuery, callback_data: ServerSelectCallback,
                                  state: FSMContext):
    message = await callback_query.message.edit_text("🔄 Меняем локацию...")
    state_data = await state.get_data()
    subscription_id = int(state_data.get("subscription_id"))

    selected_server_ip = callback_data.server_ip
    selected_server_name = callback_data.server_name

    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    if subscription_id is None:
        await callback_query.message.answer("Не удалось найти подписку. Попробуйте еще раз.")
        return

    async with DatabaseContextManager() as session_methods:
        try:
            subscription = await session_methods.subscription.get_subscription_by_id(subscription_id)
            old_key_id = subscription.key_id
            if not subscription:
                raise "Не найдена подписка в базе данных"

            session_cookie = await get_session_cookie(selected_server_ip)
            if not session_cookie:
                raise ServerUnavailableError(f"Сервер недоступен: {selected_server_ip}")

            if subscription.name_app == NameApp.OUTLINE:
                shadowsocks_manager = ShadowsocksKeyManager(selected_server_ip, session_cookie)
                key, key_id = shadowsocks_manager.manage_shadowsocks_key(
                    tg_id=str(user_id),
                    username=username,
                )
                try:
                    session_cookie = await get_session_cookie(subscription.server_ip)
                    if not session_cookie:
                        raise ServerUnavailableError("Старый сервер недоступен, ключ не может быть удален")
                    shadowsocks_manager = ShadowsocksKeyManager(subscription.server_ip, session_cookie)
                    shadowsocks_manager.delete_key(old_key_id)
                except ServerUnavailableError as e:
                    await logger.log_error(
                        f'Пользователь: @{callback_query.from_user.username}\nСервер недоступен', e)

                await session_methods.subscription.update_sub(
                        Subscriptions(
                            subscription_id=subscription_id,
                            user_id=user_id,
                            key_id=key_id,
                            key=key,
                            server_ip=selected_server_ip
                        )
                    )

            elif subscription.name_app == NameApp.VLESS:
                vless_manager = VlessKeyManager(selected_server_ip, session_cookie)
                key, key_id = vless_manager.manage_vless_key(
                    tg_id=str(user_id),
                    username=username,
                )
                try:
                    session_cookie = await get_session_cookie(subscription.server_ip)
                    if not session_cookie:
                        raise ServerUnavailableError("Старый сервер недоступен, ключ не может быть удален")
                    vless_manager = VlessKeyManager(subscription.server_ip, session_cookie)
                    vless_manager.delete_key(old_key_id)
                except ServerUnavailableError as e:
                    await logger.log_error(
                        f'Пользователь: @{callback_query.from_user.username}\nСервер недоступен', e)
                await session_methods.subscription.update_sub(
                    Subscriptions(
                        subscription_id=subscription_id,
                        user_id=user_id,
                        key_id=key_id,
                        key=key,
                        server_ip=selected_server_ip
                    )
                )

            await message.edit_text(
                text=(
                    f"Локация успешно изменена на {selected_server_name}.\n"
                    f"🔑 Новый ключ:\n"
                    f"<pre>{key}</pre>"
                ),
                parse_mode="HTML",
            )
            await message.answer(
                text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
                reply_markup=await ReplyKeyboards.get_menu_install_app()
            )
            await session_methods.session.commit()

            await state.clear()

        except ServerUnavailableError as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\nСервер недоступен', e)
            await callback_query.answer("Выберите другой сервер, этот пока что недоступен.", show_alert=True)
            await callback_query.message.delete()
        except Exception as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'Ошибка при смене сервера', e)
            await callback_query.message.edit_text(text=LEXICON_RU['error'])
