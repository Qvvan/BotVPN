from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from logger.logging_config import logger
from models.models import SubscriptionStatusEnum, Subscriptions
from outline.outline_manager.outline_manager import OutlineManager
from services.send_sms_admins import notify_group
from state.state import DeleteKey, KeyBlock, CancelSub

router = Router()


@router.message(Command(commands='cancel_sub'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь UserID, и я отменю его подписку',
        reply_markup = await InlineKeyboards.cancel(),
    )
    await state.set_state(CancelSub.waiting_user_id)


@router.message(CancelSub.waiting_user_id)
async def process_api_url(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with DatabaseContextManager() as session_methods:
        try:
            manager = OutlineManager()
            await manager.wait_for_initialization()
            sub = await session_methods.subscription.get_subscription(user_id)
            server_info = await session_methods.vpn_keys.get_by_id(sub.vpn_key_id)
            if not server_info:
                logger.error(f"Подписка есть, а ключа такого в базе нет, ошибка!")
                await notify_group(
                    message=f'ID: {sub.user_id}\n'
                            f'Подписка есть, а ключа в базе нет.\n\n'
                            f'ID подписки: {sub.subscription_id}'
                            f'ID пользователя: {sub.user_id}\n'
                            f'#подписка',
                    is_error=True
                )
                return

            await session_methods.subscription.update_sub(Subscriptions(
                user_id=sub.user_id,
                service_id=sub.service_id,
                vpn_key_id=sub.vpn_key_id,
                start_date=sub.start_date,
                end_date=sub.end_date,
                status=SubscriptionStatusEnum.EXPIRED,
            ))

            await session_methods.vpn_keys.update_limit(vpn_key_id=sub.vpn_key_id, new_limit=1)

            await manager.upd_limit(server_info.server_id, server_info.outline_key_id)
            await session_methods.session.commit()
            await message.answer('Подписка успешно отменена')

        except Exception as e:
            await session_methods.session.rollback()
            await message.answer(f'Произошла ошибка при отмене подписки:\n{e}')
            logger.error('Не удалось отменить подписку', e)

        await state.clear()