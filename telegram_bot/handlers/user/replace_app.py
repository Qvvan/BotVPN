from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.context_manager import DatabaseContextManager
from handlers.services.get_session_cookies import get_session_cookie
from handlers.services.key_create import ShadowsocksKeyManager, VlessKeyManager, ServerUnavailableError
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import NameApp, SubscriptionStatusEnum

router = Router()


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'replace_app'))
async def get_support(callback_query: CallbackQuery, state: FSMContext, callback_data: SubscriptionCallbackFactory):
    await callback_query.answer()
    subscription_id = callback_data.subscription_id
    name_app = callback_data.name_app
    async with DatabaseContextManager() as session_methods:
        try:
            subscription = await session_methods.subscription.get_subscription_by_id(subscription_id)
            if subscription.status == SubscriptionStatusEnum.EXPIRED:
                await callback_query.answer(LEXICON_RU["subscription_expired"], show_alert=True, cache_time=5)
                return
        except Exception as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'ID: {callback_query.from_user.id}\n'
                                   f'Ошибка при получении подписок', e)
            await callback_query.answer(LEXICON_RU["error"], show_alert=True, cache_time=5)
            return


    await state.update_data(subscription_id=subscription_id)

    await callback_query.message.answer(
        text=LEXICON_RU['choice_app'],
        reply_markup=await InlineKeyboards.replace_app(name_app),
        parse_mode='HTML',
    )


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == "name_app"))
async def handle_server_selection(callback_query: CallbackQuery,
                                  state: FSMContext):
    message = await callback_query.message.edit_text("🔄 Меняем приложение...")

    state_data = await state.get_data()
    subscription_id = int(state_data.get("subscription_id"))
    async with DatabaseContextManager() as session_methods:
        try:
            subscription = await session_methods.subscription.get_subscription_by_id(subscription_id)
            if subscription.status == SubscriptionStatusEnum.EXPIRED:
                await callback_query.answer(LEXICON_RU["subscription_expired"], show_alert=True, cache_time=5)
                return
        except Exception as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'ID: {callback_query.from_user.id}\n'
                                   f'Ошибка при получении подписок', e)
            await callback_query.answer(LEXICON_RU["error"], show_alert=True, cache_time=5)
            return

    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    async with DatabaseContextManager() as session_methods:
        try:
            subscription = await session_methods.subscription.get_subscription_by_id(subscription_id)
            old_key_id = subscription.key_id
            if not subscription:
                raise "Не найдена подписка в базе данных"

            session_cookie = await get_session_cookie(subscription.server_ip)
            if not session_cookie:
                raise ServerUnavailableError(f"Сервер недоступен: {subscription.server_ip}")
            if subscription.name_app == NameApp.OUTLINE:
                name_app = NameApp.VLESS
                vless_manager = VlessKeyManager(subscription.server_ip, session_cookie)
                key, key_id = await vless_manager.manage_vless_key(
                    tg_id=str(user_id),
                    username=username,
                )
                await session_methods.subscription.update_sub(
                    subscription_id=subscription_id,
                    user_id=user_id,
                    key_id=key_id,
                    name_app=name_app,
                    key=key,
                )
                await vless_manager.delete_key(old_key_id)

            elif subscription.name_app == NameApp.VLESS:
                name_app = NameApp.OUTLINE
                shadowsocks_manager = ShadowsocksKeyManager(subscription.server_ip, session_cookie)
                key, key_id = await shadowsocks_manager.manage_shadowsocks_key(
                    tg_id=str(user_id),
                    username=username,
                )
                await session_methods.subscription.update_sub(
                    subscription_id=subscription_id,
                    user_id=user_id,
                    key_id=key_id,
                    name_app=name_app,
                    key=key
                )
                await shadowsocks_manager.delete_key(old_key_id)

            await message.edit_text(
                text=(
                    f"Приложение успешно изменено на {name_app}.\n"
                    f"🔑 Новый ключ:\n"
                    f"<pre>{key}</pre>"
                ),
                parse_mode="HTML"
            )
            await message.answer(
                text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
                reply_markup=await ReplyKeyboards.get_menu_install_app()
            )
            await session_methods.session.commit()

        except ServerUnavailableError as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'ID: {callback_query.from_user.id}\n'
                                   f'Сервер недоступен', e)
            await callback_query.answer("Выберите другой сервер, этот пока что недоступен.", show_alert=True)
            await callback_query.message.delete()
        except Exception as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'ID: {callback_query.from_user.id}\n'
                                   f'Ошибка при смене приложения', e)
            await callback_query.message.edit_text(text=LEXICON_RU['error'])
        await state.clear()
