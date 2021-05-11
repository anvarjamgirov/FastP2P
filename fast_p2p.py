from requests import post


class ERROR:
    THIS_CARD_IS_NOT_SERVICED = -31900
    AMOUNT_OF_PAYMENT_IS_LESS_THAN_MINIMUM = -31611
    INCORRECT_CARD_NUMBER = -31630
    INCORRECT_MY_CARD_NUMBER = -31101
    INCORRECT_SMS_CODE = -31103
    PAYMENT_IS_OUT_OF_DATE = -31640
    NETWORK_ERROR = -50001

    MESSAGE = {
        THIS_CARD_IS_NOT_SERVICED: "Ushbu karta raqami bilan amaliyot qilib bo'lmaydi",
        AMOUNT_OF_PAYMENT_IS_LESS_THAN_MINIMUM: "O'tkazmaning eng kam miqdori 1000 so'm bo'lishi kerak",
        INCORRECT_CARD_NUMBER: "Karta raqami noto'g'ri yoki hisobda o'tkazma uchun mablag' yetarli emas.",
        INCORRECT_MY_CARD_NUMBER: "Qabul qiluvchining karta raqami xato kiritilgan.",
        INCORRECT_SMS_CODE: "SMS kod noto'g'ri kiritildi.",
        PAYMENT_IS_OUT_OF_DATE: "O'tkazma muddati eskirgan, qayta urinib ko'ring.",
        NETWORK_ERROR: "So'rov yuborishdagi xatolik."
    }


class FastP2PError(Exception):
    def __init__(self, code, message=None):
        self.code = code
        self.message = ERROR.MESSAGE.get(code) if not message else message


class Cheque:
    def __init__(self, _id: str, amount: int):
        self.id = _id
        self.amount = amount//100


class FastP2P:
    base_url = "https://payme.uz/api/fast_p2p."

    class TEXT:
        pass

    def __init__(self, card_number: str):
        self.my_card_number = card_number

    def _make_request(self, method_url, params):
        json = {
            "method": "fast_p2p." + method_url,
            "params": params
        }
        request_url = self.base_url + method_url
        try:
            response = post(
                request_url,
                json=json
            ).json()
            if response and response.get("error"):
                raise FastP2PError(response['error']['code'])
            else:
                return response['result']
        except Exception as e:
            raise FastP2PError(ERROR.NETWORK_ERROR, e.args)

    def create(self, amount: int, card_number: str, expire: str) -> Cheque:
        response = self._make_request(
            'create',
            {
                "amount": amount * 100,
                "number": self.my_card_number,
                "pay_card": {
                    "number": card_number,
                    "expire": expire
                }
            }
        )
        return Cheque(
            response['cheque']['_id'],
            response['cheque']['amount']
        )

    def get_pay_code(self, cheque_id: str) -> str:
        response = self._make_request(
            'get_pay_code',
            {
                "id": cheque_id
            }
        )
        return response['phone']

    def pay(self, cheque_id: str, code: str) -> Cheque:
        response = self._make_request(
            'pay',
            {
                "id": cheque_id,
                "code": code
            }
        )
        return Cheque(
            response['cheque']['_id'],
            response['cheque']['amount']
        )
