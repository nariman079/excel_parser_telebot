from aiogram.filters.state import State, StatesGroup


class ExcelFileState(StatesGroup):
    file = State()


class SearchInstallmentPlanState(StatesGroup):
    search_type = State()
    number = State()
    phone_number = State()


class CreateAdminUserState(StatesGroup):
    username = State()
    delete = State()


class GetContactUser(StatesGroup):
    phone_number = State()
