from aiogram.dispatcher.filters.state import StatesGroup, State


class ProjectStates(StatesGroup):
    # Отправка анкеты
    send_information_form = State()
    # Отправка истории
    send_story = State()

    # Получений анкет
    get_information_forms = State()
    # Получений историй
    get_stories = State()
