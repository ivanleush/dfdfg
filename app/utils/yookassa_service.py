# utils/yookassa_service.py
from yookassa import Payment
import logging

logger = logging.getLogger(__name__)


class YooKassaService:

    def __init__(self, shop_id, secret_key):
        # Конфигурация YooKassa
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.configure_yookassa()

    def configure_yookassa(self):
        from yookassa import Configuration
        Configuration.configure(self.shop_id, self.secret_key)

    async def get_payment_info(self, payment_id: str):
        try:
            # Получаем информацию о платеже по ID
            payment = await Payment.find_one(payment_id)
            if payment:
                logger.info(f"Платеж {payment_id} найден, статус: {payment.status}")
                return {
                    "status": payment.status,
                    "paid": payment.paid,
                    "amount_value": float(payment.amount.value),
                    "currency": payment.amount.currency
                }
            else:
                logger.error(f"Платеж {payment_id} не найден.")
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о платеже {payment_id}: {e}")
            return None
