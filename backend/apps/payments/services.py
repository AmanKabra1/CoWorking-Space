class RazorpayService:
    def __init__(self, key_id: str, key_secret: str):
        import razorpay
        self.client = razorpay.Client(auth=(key_id, key_secret))

    def create_order(self, amount_paise: int, currency: str, receipt: str) -> dict:
        return self.client.order.create({
            'amount': amount_paise,
            'currency': currency,
            'receipt': receipt,
        })

    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        self.client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
        return True


class StripeService:
    def __init__(self, secret_key: str):
        import stripe as _stripe
        self._stripe = _stripe
        self._stripe.api_key = secret_key

    def create_payment_intent(self, amount_cents: int, currency: str, metadata: dict) -> object:
        return self._stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            metadata=metadata,
        )

    def verify_webhook(self, payload: bytes, sig_header: str, endpoint_secret: str) -> object:
        return self._stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
