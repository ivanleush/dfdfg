import httpx
import logging
from app.config import settings

TON_TO_RUB_EXCHANGE_RATE = 200

logger = logging.getLogger(__name__)


class CryptoPaymentService:
    def __init__(self):
        self.api_url = "https://pay.crypt.bot/api/"
        self.headers = {
            'Crypto-Pay-API-Token': settings.CRYPTO_BOT_TOKEN
        }

    async def create_invoice(self, amount: float, user_id: int) -> dict | None:
        """Создает счет для оплаты в TON (можно изменить на USDT)."""
        url = f"{self.api_url}createInvoice"
        payload = {
            'asset': 'TON',  # Или 'USDT'
            'amount': str(amount),
            'description': f'Пополнение баланса',
            'payload': str(user_id)
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
                response.raise_for_status()
                result = response.json()

                if result.get('ok'):
                    return result.get('result')
                else:
                    logger.error(f"Ошибка при создании счета: {result.get('error', 'Unknown error')}")
                    return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при создании счета: {e}")
            return None
        except Exception as e:
            logger.error(f"Исключение при создании счета: {e}")
            return None

    async def check_invoice_status(self, invoice_id: int) -> str | None:
        """Проверяет статус счета."""
        url = f"{self.api_url}getInvoices"
        params = {
            'invoice_ids': str(invoice_id)
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                result = response.json()

                if result.get('ok') and result['result']['items']:
                    return result['result']['items'][0].get('status', 'unknown')
                else:
                    return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при проверке счета: {e}")
            return None
        except Exception as e:
            logger.error(f"Исключение при проверке счета: {e}")
            return None