import os
from typing import List, Optional, Union, Dict
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    BOT_TOKEN: str
    ADMIN_IDS: str
    SUPPORT_USERNAME: str = "@support"

    BOT_USERNAME: str = "@sdfsdgsdgsdgsdgsrobot"

    WHEEL_OF_FORTUNE_ENABLED: bool = True
    WHEEL_OF_FORTUNE_COOLDOWN_HOURS: int = 24
    WHEEL_OF_FORTUNE_REWARDS: str = "0:30,5:40,10:20,20:8,50:2"

    ADMIN_NOTIFICATIONS_ENABLED: bool = False
    ADMIN_NOTIFICATIONS_CHAT_ID: Optional[str] = None
    ADMIN_NOTIFICATIONS_TOPIC_ID: Optional[int] = None

    CRYPTO_BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    CHANNEL_SUB_ID: Optional[str] = None
    CHANNEL_LINK: Optional[str] = None
    CHANNEL_IS_REQUIRED_SUB: bool = False
    CHANNEL_IS_SUB_REQUIRED: bool = False
    
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    FORTUNE_WHEEL_OUTCOMES: List[dict] = [  # Вот здесь нужно добавить : List[dict]
        {
            "name": "Lose",
            "weight": 50,
            "min_amount_kopeks": 0,
            "max_amount_kopeks": 0
        },
        {
            "name": "Small Win",
            "weight": 35,
            "min_amount_kopeks": 100,
            "max_amount_kopeks": 500
        },
        {
            "name": "Medium Win",
            "weight": 10,
            "min_amount_kopeks": 500,
            "max_amount_kopeks": 1000
        },
        {
            "name": "Big Win",
            "weight": 5,
            "min_amount_kopeks": 1000,
            "max_amount_kopeks": 5000
        }
    ]

    # ID каналов для проверки подписки
    SUBSCRIPTION_CHANNEL_IDS: list[str] = ["-1002896743504"]

    # Информация о каналах для отображения
    SUBSCRIPTION_CHANNELS: list[dict] = [
        {
            "name": "Основной канал",
            "url": "https://t.me/proverkatestpodp"
        }
    ]

    REMNAWAVE_API_URL: str
    REMNAWAVE_API_KEY: str
    REMNAWAVE_SECRET_KEY: Optional[str] = None
    
    TRIAL_DURATION_DAYS: int = 3
    TRIAL_TRAFFIC_LIMIT_GB: int = 10
    TRIAL_DEVICE_LIMIT: int = 2
    DEFAULT_TRAFFIC_LIMIT_GB: int = 100
    DEFAULT_DEVICE_LIMIT: int = 1
    TRIAL_SQUAD_UUID: str
    DEFAULT_TRAFFIC_RESET_STRATEGY: str = "MONTH"
    MAX_DEVICES_LIMIT: int = 20
    
    TRIAL_WARNING_HOURS: int = 2 
    ENABLE_NOTIFICATIONS: bool = True 
    NOTIFICATION_RETRY_ATTEMPTS: int = 3 
    
    MONITORING_LOGS_RETENTION_DAYS: int = 30 
    NOTIFICATION_CACHE_HOURS: int = 24  
    
    BASE_SUBSCRIPTION_PRICE: int = 50000

    AVAILABLE_SUBSCRIPTION_PERIODS: str = "14,30,60,90,180,360"
    AVAILABLE_RENEWAL_PERIODS: str = "30,90,180"
    PRICE_14_DAYS: int = 50000
    PRICE_30_DAYS: int = 99000
    PRICE_60_DAYS: int = 189000
    PRICE_90_DAYS: int = 269000
    PRICE_180_DAYS: int = 499000
    PRICE_360_DAYS: int = 899000
    
    PRICE_TRAFFIC_5GB: int = 2000
    PRICE_TRAFFIC_10GB: int = 3500
    PRICE_TRAFFIC_25GB: int = 7000
    PRICE_TRAFFIC_50GB: int = 11000
    PRICE_TRAFFIC_100GB: int = 15000
    PRICE_TRAFFIC_250GB: int = 17000
    PRICE_TRAFFIC_500GB: int = 19000
    PRICE_TRAFFIC_1000GB: int = 19500
    PRICE_TRAFFIC_UNLIMITED: int = 20000
    
    TRAFFIC_PACKAGES_CONFIG: str = ""
    
    PRICE_PER_DEVICE: int = 5000
    
    TRAFFIC_SELECTION_MODE: str = "selectable" 
    FIXED_TRAFFIC_LIMIT_GB: int = 100 
    
    REFERRAL_MINIMUM_TOPUP_KOPEKS: int = 10000 
    REFERRAL_FIRST_TOPUP_BONUS_KOPEKS: int = 10000 
    REFERRAL_INVITER_BONUS_KOPEKS: int = 10000 
    REFERRAL_COMMISSION_PERCENT: int = 25 

    REFERRAL_NOTIFICATIONS_ENABLED: bool = True
    REFERRAL_NOTIFICATION_RETRY_ATTEMPTS: int = 3
    REFERRED_USER_REWARD: int = 0 
    
    AUTOPAY_WARNING_DAYS: str = "3,24"
    
    DEFAULT_AUTOPAY_DAYS_BEFORE: int = 3 
    MIN_BALANCE_FOR_AUTOPAY_KOPEKS: int = 10000  
    
    MONITORING_INTERVAL: int = 60
    INACTIVE_USER_DELETE_MONTHS: int = 3

    MAINTENANCE_MODE: bool = False
    MAINTENANCE_CHECK_INTERVAL: int = 30 
    MAINTENANCE_AUTO_ENABLE: bool = True 
    MAINTENANCE_MESSAGE: str = "🔧 Ведутся технические работы. Сервис временно недоступен. Попробуйте позже."
    
    TELEGRAM_STARS_ENABLED: bool = True
    TELEGRAM_STARS_RATE_RUB: float = 1.3
    
    TRIBUTE_ENABLED: bool = False
    TRIBUTE_API_KEY: Optional[str] = None
    TRIBUTE_DONATE_LINK: Optional[str] = None
    TRIBUTE_WEBHOOK_PATH: str = "/tribute-webhook"
    TRIBUTE_WEBHOOK_PORT: int = 8081

    YOOKASSA_ENABLED: bool = False
    YOOKASSA_SHOP_ID: Optional[str] = None
    YOOKASSA_SECRET_KEY: Optional[str] = None
    YOOKASSA_RETURN_URL: Optional[str] = None
    YOOKASSA_DEFAULT_RECEIPT_EMAIL: Optional[str] = None
    YOOKASSA_VAT_CODE: int = 1 
    YOOKASSA_PAYMENT_MODE: str = "full_payment" 
    YOOKASSA_PAYMENT_SUBJECT: str = "service"
    YOOKASSA_WEBHOOK_PATH: str = "/yookassa-webhook"
    YOOKASSA_WEBHOOK_PORT: int = 8082
    YOOKASSA_WEBHOOK_SECRET: Optional[str] = None
    PAYMENT_BALANCE_DESCRIPTION: str = "Пополнение баланса"
    PAYMENT_SUBSCRIPTION_DESCRIPTION: str = "Оплата подписки"
    PAYMENT_SERVICE_NAME: str = "Интернет-сервис"
    PAYMENT_BALANCE_TEMPLATE: str = "{service_name} - {description}"
    PAYMENT_SUBSCRIPTION_TEMPLATE: str = "{service_name} - {description}"


    CONNECT_BUTTON_MODE: str = "guide"
    MINIAPP_CUSTOM_URL: str = ""
    
    DEFAULT_LANGUAGE: str = "ru"
    AVAILABLE_LANGUAGES: str = "ru,en"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bot.log"
    
    DEBUG: bool = False
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook"
    
    APP_CONFIG_PATH: str = "app-config.json"
    ENABLE_DEEP_LINKS: bool = True
    APP_CONFIG_CACHE_TTL: int = 3600
    
    # Настройки версионирования
    VERSION_CHECK_REPO: str = "fr1ngg/remnawave-bedolaga-telegram-bot"
    VERSION_CHECK_ENABLED: bool = True

    def get_wheel_of_fortune_rewards(self) -> List[Dict]:
        """Возвращает список наград для колеса фортуны"""
        rewards = []
        try:
            rewards_config = self.WHEEL_OF_FORTUNE_REWARDS.strip()
            if not rewards_config:
                return self._get_default_wheel_rewards()

            for reward_config in rewards_config.split(','):
                reward_config = reward_config.strip()
                if not reward_config:
                    continue

                parts = reward_config.split(':')
                if len(parts) != 2:
                    continue

                try:
                    amount = int(parts[0])
                    chance = int(parts[1])

                    rewards.append({
                        "amount": amount,
                        "chance": chance
                    })
                except ValueError:
                    continue

            return rewards if rewards else self._get_default_wheel_rewards()

        except Exception:
            return self._get_default_wheel_rewards()

    def _get_default_wheel_rewards(self) -> List[Dict]:
        """Возвращает настройки по умолчанию для колеса фортуны"""
        return [
            {"amount": 0, "chance": 30},
            {"amount": 5, "chance": 40},
            {"amount": 10, "chance": 20},
            {"amount": 20, "chance": 8},
            {"amount": 50, "chance": 2}
        ]

    def is_wheel_of_fortune_enabled(self) -> bool:
        return self.WHEEL_OF_FORTUNE_ENABLED

    def get_wheel_cooldown_hours(self) -> int:
        return self.WHEEL_OF_FORTUNE_COOLDOWN_HOURS

    @field_validator('LOG_FILE', mode='before')
    @classmethod
    def ensure_log_dir(cls, v):
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)
    
    def is_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        """
        try:
            # ✅ Преобразуем строку с ID в список чисел
            admin_list = [int(uid.strip()) for uid in self.ADMIN_IDS.split(',')]
            return user_id in admin_list
        except (ValueError, AttributeError):
            # Обработка ошибки, если .env файл пустой или содержит неверные данные
            return False
    
    def get_admin_ids(self) -> List[int]:
        try:
            admin_ids = self.ADMIN_IDS
            
            if isinstance(admin_ids, str):
                if not admin_ids.strip():
                    return []
                return [int(x.strip()) for x in admin_ids.split(',') if x.strip()]
            
            return []
            
        except (ValueError, AttributeError):
            return []
    
    def get_autopay_warning_days(self) -> List[int]:
        try:
            days = self.AUTOPAY_WARNING_DAYS
            if isinstance(days, str):
                if not days.strip():
                    return [3, 1]
                return [int(x.strip()) for x in days.split(',') if x.strip()]
            return [3, 1]
        except (ValueError, AttributeError):
            return [3, 1]
    
    def get_available_languages(self) -> List[str]:
        try:
            langs = self.AVAILABLE_LANGUAGES
            if isinstance(langs, str):
                if not langs.strip():
                    return ["ru", "en"]
                return [x.strip() for x in langs.split(',') if x.strip()]
            return ["ru", "en"]
        except AttributeError:
            return ["ru", "en"]
    
    def format_price(self, price_kopeks: int) -> str:
        rubles = price_kopeks / 100
        return f"{rubles:.2f} ₽"
    
    def kopeks_to_rubles(self, kopeks: int) -> float:
        return kopeks / 100
    
    def rubles_to_kopeks(self, rubles: float) -> int:
        return int(rubles * 100)
    
    def get_trial_warning_hours(self) -> int:
        return self.TRIAL_WARNING_HOURS
    
    def is_notifications_enabled(self) -> bool:
        return self.ENABLE_NOTIFICATIONS
    
    def get_app_config_path(self) -> str:
        if os.path.isabs(self.APP_CONFIG_PATH):
            return self.APP_CONFIG_PATH
        
        project_root = Path(__file__).parent.parent
        return str(project_root / self.APP_CONFIG_PATH)
    
    def is_deep_links_enabled(self) -> bool:
        return self.ENABLE_DEEP_LINKS
    
    def get_app_config_cache_ttl(self) -> int:
        return self.APP_CONFIG_CACHE_TTL
    
    def is_traffic_selectable(self) -> bool:
        return self.TRAFFIC_SELECTION_MODE.lower() == "selectable"
    
    def is_traffic_fixed(self) -> bool:
        return self.TRAFFIC_SELECTION_MODE.lower() == "fixed"
    
    def get_fixed_traffic_limit(self) -> int:
        return self.FIXED_TRAFFIC_LIMIT_GB
    
    def is_yookassa_enabled(self) -> bool:
        return (self.YOOKASSA_ENABLED and 
                self.YOOKASSA_SHOP_ID is not None and 
                self.YOOKASSA_SECRET_KEY is not None)
    
    def get_yookassa_return_url(self) -> str:
        if self.YOOKASSA_RETURN_URL:
            return self.YOOKASSA_RETURN_URL
        elif self.WEBHOOK_URL:
            return f"{self.WEBHOOK_URL}/payment-success"
        return "https://t.me/"

    def is_maintenance_mode(self) -> bool:
        return self.MAINTENANCE_MODE
    
    def get_maintenance_message(self) -> str:
        return self.MAINTENANCE_MESSAGE
    
    def get_maintenance_check_interval(self) -> int:
        return self.MAINTENANCE_CHECK_INTERVAL
    
    def is_maintenance_auto_enable(self) -> bool:
        return self.MAINTENANCE_AUTO_ENABLE

    def get_available_subscription_periods(self) -> List[int]:
        try:
            periods_str = self.AVAILABLE_SUBSCRIPTION_PERIODS
            if not periods_str.strip():
                return [30, 90, 180] 
            
            periods = []
            for period_str in periods_str.split(','):
                period_str = period_str.strip()
                if period_str:
                    period = int(period_str)
                    if period in PERIOD_PRICES:
                        periods.append(period)
            
            return periods if periods else [30, 90, 180]
            
        except (ValueError, AttributeError):
            return [30, 90, 180]
    
    def get_available_renewal_periods(self) -> List[int]:
        try:
            periods_str = self.AVAILABLE_RENEWAL_PERIODS
            if not periods_str.strip():
                return [30, 90, 180] 
            
            periods = []
            for period_str in periods_str.split(','):
                period_str = period_str.strip()
                if period_str:
                    period = int(period_str)
                    if period in PERIOD_PRICES:
                        periods.append(period)
            
            return periods if periods else [30, 90, 180]
            
        except (ValueError, AttributeError):
            return [30, 90, 180]

    def get_balance_payment_description(self, amount_kopeks: int) -> str:
        return self.PAYMENT_BALANCE_TEMPLATE.format(
            service_name=self.PAYMENT_SERVICE_NAME,
            description=f"{self.PAYMENT_BALANCE_DESCRIPTION} на {self.format_price(amount_kopeks)}"
        )
    
    def get_subscription_payment_description(self, period_days: int, amount_kopeks: int) -> str:
        return self.PAYMENT_SUBSCRIPTION_TEMPLATE.format(
            service_name=self.PAYMENT_SERVICE_NAME,
            description=f"{self.PAYMENT_SUBSCRIPTION_DESCRIPTION} на {period_days} дней"
        )
    
    def get_custom_payment_description(self, description: str) -> str:
        return self.PAYMENT_BALANCE_TEMPLATE.format(
            service_name=self.PAYMENT_SERVICE_NAME,
            description=description
        )

    def get_stars_rate(self) -> float:
        return self.TELEGRAM_STARS_RATE_RUB
    
    def stars_to_rubles(self, stars: int) -> float:
        return stars * self.get_stars_rate()
    
    def rubles_to_stars(self, rubles: float) -> int:
        return max(1, int(rubles / self.get_stars_rate()))

    def get_admin_notifications_chat_id(self) -> Optional[int]:
        if not self.ADMIN_NOTIFICATIONS_CHAT_ID:
            return None
        
        try:
            return int(self.ADMIN_NOTIFICATIONS_CHAT_ID)
        except (ValueError, TypeError):
            return None
    
    def is_admin_notifications_enabled(self) -> bool:
        return (self.ADMIN_NOTIFICATIONS_ENABLED and 
                self.get_admin_notifications_chat_id() is not None)

    def get_referral_settings(self) -> Dict:
        return {
            "minimum_topup_kopeks": self.REFERRAL_MINIMUM_TOPUP_KOPEKS,
            "first_topup_bonus_kopeks": self.REFERRAL_FIRST_TOPUP_BONUS_KOPEKS,
            "inviter_bonus_kopeks": self.REFERRAL_INVITER_BONUS_KOPEKS,
            "commission_percent": self.REFERRAL_COMMISSION_PERCENT,
            "notifications_enabled": self.REFERRAL_NOTIFICATIONS_ENABLED,
            "referred_user_reward": self.REFERRED_USER_REWARD
        }
    
    def is_referral_notifications_enabled(self) -> bool:
        return self.REFERRAL_NOTIFICATIONS_ENABLED
    
    def get_traffic_packages(self) -> List[Dict]:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            packages = []
            config_str = self.TRAFFIC_PACKAGES_CONFIG.strip()
            
            logger.info(f"CONFIG STRING: '{config_str}'")
            
            if not config_str:
                logger.info("CONFIG EMPTY, USING FALLBACK")
                return self._get_fallback_traffic_packages()
            
            logger.info("PARSING CONFIG...")
            
            for package_config in config_str.split(','):
                package_config = package_config.strip()
                if not package_config:
                    continue
                    
                parts = package_config.split(':')
                if len(parts) != 3:
                    continue
                    
                try:
                    gb = int(parts[0])
                    price = int(parts[1])
                    enabled = parts[2].lower() == 'true'
                    
                    packages.append({
                        "gb": gb,
                        "price": price,
                        "enabled": enabled
                    })
                except ValueError:
                    continue
            
            logger.info(f"PARSED {len(packages)} packages from config")
            return packages if packages else self._get_fallback_traffic_packages()
            
        except Exception as e:
            logger.info(f"ERROR PARSING CONFIG: {e}")
            return self._get_fallback_traffic_packages()
    
    def _get_fallback_traffic_packages(self) -> List[Dict]:
        try:
            if self.TRAFFIC_PACKAGES_CONFIG.strip():
                packages = []
                for package_config in self.TRAFFIC_PACKAGES_CONFIG.split(','):
                    package_config = package_config.strip()
                    if not package_config:
                        continue
                        
                    parts = package_config.split(':')
                    if len(parts) != 3:
                        continue
                        
                    try:
                        gb = int(parts[0])
                        price = int(parts[1])
                        enabled = parts[2].lower() == 'true'
                        
                        packages.append({
                            "gb": gb,
                            "price": price,
                            "enabled": enabled
                        })
                    except ValueError:
                        continue
                
                if packages:
                    return packages
        except Exception as e:
            pass
        
        return [
            {"gb": 5, "price": self.PRICE_TRAFFIC_5GB, "enabled": True},
            {"gb": 10, "price": self.PRICE_TRAFFIC_10GB, "enabled": True},
            {"gb": 25, "price": self.PRICE_TRAFFIC_25GB, "enabled": True},
            {"gb": 50, "price": self.PRICE_TRAFFIC_50GB, "enabled": True},
            {"gb": 100, "price": self.PRICE_TRAFFIC_100GB, "enabled": True},
            {"gb": 250, "price": self.PRICE_TRAFFIC_250GB, "enabled": True},
            {"gb": 500, "price": self.PRICE_TRAFFIC_500GB, "enabled": True},
            {"gb": 1000, "price": self.PRICE_TRAFFIC_1000GB, "enabled": True},
            {"gb": 0, "price": self.PRICE_TRAFFIC_UNLIMITED, "enabled": True}, 
        ]
    
    def get_traffic_price(self, gb: int) -> int:
        packages = self.get_traffic_packages()
        
        for package in packages:
            if package["gb"] == gb and package["enabled"]:
                return package["price"]
        
        
        enabled_packages = [pkg for pkg in packages if pkg["enabled"]]
        if not enabled_packages:
            return 0
        
        unlimited_package = next((pkg for pkg in enabled_packages if pkg["gb"] == 0), None)
        
        finite_packages = [pkg for pkg in enabled_packages if pkg["gb"] > 0]
        if finite_packages:
            max_package = max(finite_packages, key=lambda x: x["gb"])
            
            if gb > max_package["gb"]:
                if unlimited_package:
                    return unlimited_package["price"]
                else:
                    return max_package["price"]
            
            suitable_packages = [pkg for pkg in finite_packages if pkg["gb"] >= gb]
            if suitable_packages:
                nearest_package = min(suitable_packages, key=lambda x: x["gb"])
                return nearest_package["price"]
        
        if unlimited_package:
            return unlimited_package["price"]
        
        return 0
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


settings = Settings()


PERIOD_PRICES = {
    14: settings.PRICE_14_DAYS,
    30: settings.PRICE_30_DAYS,
    60: settings.PRICE_60_DAYS,
    90: settings.PRICE_90_DAYS,
    180: settings.PRICE_180_DAYS,
    360: settings.PRICE_360_DAYS,
}



def get_traffic_prices() -> Dict[int, int]:
    packages = settings.get_traffic_packages()
    return {package["gb"]: package["price"] for package in packages}

TRAFFIC_PRICES = get_traffic_prices()

def refresh_traffic_prices():
    global TRAFFIC_PRICES
    TRAFFIC_PRICES = get_traffic_prices()

refresh_traffic_prices()
