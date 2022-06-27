from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup


class DialogState(State):
    """Состояние для анонимного диалога."""

    async def set(self, chat_id=None, user_id=None, data=None):
        state = Dispatcher.get_current().current_state(
            chat=chat_id, user=user_id)

        if data:
            await state.set_data(data)

        await state.set_state(self.state)


class ProjectStates(StatesGroup):
    # Отправка анкеты
    send_information_form = State()
    # Отправка истории
    send_story = State()

    # Получений анкет
    get_information_forms = State()
    # Получений историй
    get_stories = State()

    # Состояние ввода сообщения от админа, для редактирования анкеты
    need_to_edit_person_info = State()
    # Состояние ввода сообщения от админа, для редактирования истории
    need_to_edit_story = State()

    # Состояние поиска анонимного диалога
    search_anon_dialog_state = State()
    # Состояние анонимного диалога
    anon_dialog_state = DialogState()
