from aiogram.fsm.state import StatesGroup, State

from aiogram.fsm.state import State, StatesGroup

class WithdrawStates(StatesGroup):
    get_amount = State()
    get_requisites = State()

class RegistrationStates(StatesGroup):
    waiting_for_rules_accept = State()
    waiting_for_referral_code = State()
    waiting_for_subscription = State()  # Новое состояние для ожидания подписки

class SubscriptionStates(StatesGroup):
    selecting_period = State()
    selecting_traffic = State()
    selecting_countries = State()
    selecting_devices = State()
    confirming_purchase = State()
    
    adding_countries = State()
    adding_traffic = State()
    adding_devices = State()
    extending_subscription = State()
    confirming_traffic_reset = State()


class BalanceStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_stars_payment = State()
    waiting_for_support_request = State()


class PromoCodeStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_referral_code = State()


class AdminStates(StatesGroup):
    
    waiting_for_user_search = State()
    editing_user_balance = State()
    extending_subscription = State()
    adding_traffic = State()
    granting_subscription = State()
    editing_user_subscription = State()
    
    creating_promocode = State()
    setting_promocode_type = State()
    setting_promocode_value = State()
    setting_promocode_uses = State()
    setting_promocode_expiry = State()
    
    waiting_for_broadcast_message = State()
    confirming_broadcast = State()
    
    editing_squad_price = State()
    editing_traffic_price = State()
    editing_device_price = State()
    editing_user_devices = State()
    editing_user_traffic = State()
    
    editing_rules_page = State()
    
    confirming_sync = State()

    editing_server_name = State()
    editing_server_price = State()
    editing_server_country = State()
    editing_server_limit = State()
    editing_server_description = State()
    
    creating_server_uuid = State()
    creating_server_name = State()
    creating_server_price = State()
    creating_server_country = State()


class SupportStates(StatesGroup):
    waiting_for_message = State()


class AutoPayStates(StatesGroup):
    setting_autopay_days = State()
    confirming_autopay_toggle = State()

class SquadCreateStates(StatesGroup):
    waiting_for_name = State()
    selecting_inbounds = State()

class SquadRenameStates(StatesGroup):
    waiting_for_new_name = State()

class TaskCreationStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_reward = State()
    waiting_for_channels = State()