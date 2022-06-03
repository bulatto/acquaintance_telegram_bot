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

    # Состояние ввода сообщения от админа, для редактирования анкеты
    need_to_edit_person_info = State()
    # Состояние ввода сообщения от админа, для редактирования истории
    need_to_edit_story = State()
