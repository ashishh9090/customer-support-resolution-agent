# Payment Troubleshooting Guide
Doc ID: FAQ-PAY-005
Last Revised: 2026-03-01
Applicable Tenants: ALL

## 1. Common Reasons for Payment Declines
- **Insufficient Funds (`ERR_INSUFFICIENT_FUNDS`)**: The issuing account lacks available credit or funds.
- **Card Security Code Mismatch (`ERR_CVV_MISMATCH`)**: The CVV or expiration date entered does not match card records.
- **Billing ZIP Code Error (`ERR_AVS_FAILED`)**: The billing address does not match the address registered with the bank.
- **Bank Security Block (`ERR_FRAUD_TRIGGER`)**: High-value or international transactions flagged by the cardholder's bank anti-fraud filter.

## 2. Steps to Resolve a Failed Payment
1. Contact your card-issuing bank to authorize charges from our merchant gateway.
2. Confirm that international and e-commerce purchases are enabled on your card.
3. Attempt payment using an alternative payment method (e.g. PayPal, Apple Pay, or another debit/credit card).
4. Clear browser cookies and ensure no VPN is altering your billing location headers.

## 3. Pending Bank Authorizations vs Actual Charges
- If a checkout attempts fails, you may see a temporary pending authorization on your banking app.
- Pending authorizations are held by your card issuer and automatically drop off within 24 to 72 hours without funds being captured.
- Our merchant gateway only settles transactions with status `CAPTURED` or `SETTLED`.

## 4. Refund Timeline for Cancelled Pre-Authorizations
- Pre-authorizations for canceled orders are released immediately on our side; bank release time ranges from 1-3 business days.
