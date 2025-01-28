
# from .models import CustomerVendor, Wallet
# from authentication.models import Vendor
# import random, string


# def generate_referral_code():
#         """Generate a random 6-character referral code."""
#         return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# # customervendorfunc.delay(customer_id, business_name, referral_code)
# def customervendorfunc(customer_id, business_name, referral_code):
    
#     # payload = {
        
#     # }
#     # response = requests.post(
#     #         'http://127.0.0.1:8000/api/customer-data/',
#     #         json=payload,
#     #         headers={'Content-Type': 'application/json'}

#     #     )
#      # Validate Vendor
#             try:
#                 vendor = Vendor.objects.get(business_name=business_name)
#             except Vendor.DoesNotExist:
#                 raise ValueError ({"error": "Business name is invalid."})
#             print(vendor)
#             # Create or retrieve CustomerVendor
#             customer_vendor, created = CustomerVendor.objects.get_or_create(
#                 customerid=customer_id,
#                 vendorkey=vendor
#             )
#             print(created)
#             # If new customer, generate a referral code
#             if created:
#                 referral_code_generated = generate_referral_code()
#                 customer_vendor.referral_code = referral_code_generated
#                 customer_vendor.save()

#                 # Create wallet for new customer
#                 wallet = Wallet.objects.create(customer_vendor=customer_vendor, coins=20)
#                 message = f"Welcome! You have been awarded 20 coins as a signup bonus. Your referral code is {referral_code_generated}."
#             else:
#                 wallet, wallet_created = Wallet.objects.get_or_create(customer_vendor=customer_vendor)
#                 message = f"Welcome back! You currently have {wallet.coins} coins."

#             # Handle referral code if provided
#             if referral_code:
#                 try:
#                     referrer = CustomerVendor.objects.get(referral_code=referral_code)
#                     referrer_wallet, _ = Wallet.objects.get_or_create(customer_vendor=referrer)

#                     # Award coins to both referrer and new customer
#                     wallet.coins += 10  # Add 10 coins to the new customer for using the referral code
#                     wallet.save()

#                     referrer_wallet.coins += 5  # Add 5 coins to the referrer for referring
#                     referrer_wallet.save()

#                     message += f" You have used a referral code. Both you and the referrer have received coins."

#                 except CustomerVendor.DoesNotExist:
#                     return ({"error": "Referral code is invalid."})