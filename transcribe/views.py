# import os
# import uuid
# import subprocess
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from .whisper_utils import transcribe_audio

# @csrf_exempt
# @require_POST
# def transcribe(request):
#     if 'audio' not in request.FILES:
#         return JsonResponse({'error': 'No audio file provided'}, status=400)

#     audio_file = request.FILES['audio']
#     temp_audio_file = f'temp_audio_{uuid.uuid4().hex}.wav'  # Adjust file extension as needed

#     try:
#         # Save the uploaded audio file to a temporary file
#         with open(temp_audio_file, 'wb+') as destination:
#             for chunk in audio_file.chunks():
#                 destination.write(chunk)

#         # Transcribe the audio
#         transcription = transcribe_audio(temp_audio_file)

#         # Clean up temporary files
#         os.remove(temp_audio_file)

#         if transcription is None:
#             return JsonResponse({'error': 'Transcription failed'}, status=500)

#         return JsonResponse({'text': transcription})

#     except Exception as e:
#         # Clean up temporary files if an exception occurs
#         if os.path.isfile(temp_audio_file):
#             os.remove(temp_audio_file)
#         return JsonResponse({'error': str(e)}, status=500)

#########################################################
# import firebase_admin
# from firebase_admin import firestore
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.http import JsonResponse
# from .whisper_utils import transcribe_audio
# import os
# import uuid
# from .models import Category, MenuItem
# import logging
# from rest_framework import status
# # Initialize Firestore
# db = firestore.client()

# logger = logging.getLogger(__name__)

# @api_view(['GET'])
# def fetch_category_menu(request):
#     # Get the 'category' from the GET requestS
#     category = request.GET.get('category')
    
#     if not category:
#         return JsonResponse({"message": "Category is required", "status": "error"}, status=400)
    
#     try:
#         # Dynamically access the collection based on the category
#         menu_items_ref = db.collection(category)  # Access the Firestore collection with the category name
#         menu_items = menu_items_ref.stream()  # Fetch all documents within the collection
        
#         data = []
#         for item in menu_items:
#             item_dict = item.to_dict()
#             data.append({
#                 'name': item_dict.get('name'),
#                 'price': item_dict.get('price'),
#                 'image': item_dict.get('image'),
#                 'description': item_dict.get('description'),# Assuming you want to return the image URL too
#             })

#         if data:
#             return JsonResponse(data, safe=False)
#         else:
#             return JsonResponse({"message": f"Category \"{category}\" not found", "status": "error"}, status=404)
    
#     except Exception as e:
#         logger.error(f"Error fetching {category} data: {str(e)}")
#         return JsonResponse({"message": f"Error fetching {category} data: {str(e)}", "status": "error"}, status=500)


# @api_view(['POST'])
# def transcribe(request):
#     if 'audio' not in request.FILES:
#         return JsonResponse({'error': 'No audio file provided'}, status=400)

#     # Save the uploaded audio file temporarily
#     audio_file = request.FILES['audio']
#     temp_audio_file = f'temp_audio_{uuid.uuid4().hex}.wav'

#     try:
#         with open(temp_audio_file, 'wb+') as destination:
#             for chunk in audio_file.chunks():
#                 destination.write(chunk)

#         # Transcribe the audio file using the Whisper model
#         transcription = transcribe_audio(temp_audio_file)
#         os.remove(temp_audio_file)  # Remove the temporary file after transcription

#         if transcription is None:
#             return JsonResponse({'error': 'Transcription failed'}, status=500)

#         # Lowercase the transcription to handle cases like 'open' or 'Open'
#         transcription = transcription.lower()

#         if "open" in transcription:
#             # Extract the category from the transcription, e.g., "open pasta"
#             category = transcription.replace("open", "").strip().title()

#             # Modify the request's GET parameters to include the category for fetching the menu
#             request._request.GET = request._request.GET.copy()  # Clone the GET parameters
#             request._request.GET['category'] = category  # Set the category as a GET parameter

#             # Call the fetch_category_menu function to get the menu based on the category
#             return fetch_category_menu(request._request)

#         return JsonResponse({"text": transcription}, status=200)

#     except Exception as e:
#         if os.path.isfile(temp_audio_file):
#             os.remove(temp_audio_file)  # Clean up the file in case of an error
#         return JsonResponse({'error': str(e)}, status=500)


# def add_to_cart(request):
#     user_id = request.data.get('userId')
#     item = request.data.get('item')

#     if not user_id or not item:
#         return Response({'error': 'userId and item are required'}, status=status.HTTP_400_BAD_REQUEST)

#     cart_ref = db.collection('carts').document(user_id)
#     cart_doc = cart_ref.get()

#     if cart_doc.exists:
#         cart_data = cart_doc.to_dict()
#         items = cart_data.get('items', [])

#         # Check if the item is already in the cart
#         existing_item = next((i for i in items if i['id'] == item['id']), None)
#         if existing_item:
#             existing_item['quantity'] += 1  # Update quantity
#             cart_ref.update({'items': items})
#         else:
#             items.append({**item, 'quantity': 1})  # Add new item
#             cart_ref.set({'items': items}, merge=True)
#     else:
#         # Create a new cart if it doesn't exist
#         cart_ref.set({'items': [{**item, 'quantity': 1}]})

#     return Response({'message': 'Item added to cart successfully!'}, status=status.HTTP_200_OK)

###################################################################
import firebase_admin
from firebase_admin import firestore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from .whisper_utils import transcribe_audio
import os
import uuid
from .models import Category, MenuItem, Item
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfilePictureSerializer
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
import hmac
# from .utils import generate_signature
import datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
import hashlib
import stripe
from .models import Transaction,VoiceSample
from rest_framework.views import APIView
from resemblyzer import VoiceEncoder, preprocess_wav
import soundfile as sf
from django.core.files.storage import default_storage
import numpy as np
from .serializers import VoiceSampleSerializer
from .resemblyzer_utils import process_audio, save_embeddings_to_firebase, get_registered_embedding, compare_embeddings, check_enrollment_status
from uuid import uuid4
from scipy.spatial.distance import cosine
from firebase_admin import auth
from django.http import HttpResponse,HttpResponseRedirect
from nanoid import generate
from django.core.exceptions import DisallowedRedirect

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
# from .serializers import ProfilePictureSerializer
# from rest_framework.views import APIView
# Initialize Firestore
db = firestore.client()

logger = logging.getLogger(__name__)

# @api_view(['GET'])
# def fetch_category_menu(request):
#     # Get the 'category' from the GET request
#     category = request.GET.get('category')
    
#     if not category:
#         return JsonResponse({"message": "Category is required", "status": "error"}, status=400)
    
#     try:
#         # Dynamically access the collection based on the category
#         menu_items_ref = db.collection(category)  # Access the Firestore collection with the category name
#         menu_items = menu_items_ref.stream()  # Fetch all documents within the collection
        
#         data = []
#         for item in menu_items:
#             item_dict = item.to_dict()
#             data.append({
#                 'name': item_dict.get('name'),
#                 'price': item_dict.get('price'),
#                 'image': item_dict.get('image'),
#                 'description': item_dict.get('description'),  # Assuming you want to return the image URL too
#             })

#         if data:
#             return JsonResponse(data, safe=False)
#         else:
#             return JsonResponse({"message": f"Category \"{category}\" not found", "status": "error"}, status=404)
    
#     except Exception as e:
#         logger.error(f"Error fetching {category} data: {str(e)}")
#         return JsonResponse({"message": f"Error fetching {category} data: {str(e)}", "status": "error"}, status=500)

from firebase_admin import firestore
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
# Firestore DB reference
db = firestore.client()

@api_view(['GET'])
def fetch_category_menu(request):
    """
    Fetch menu items dynamically based on the provided category.
    Example: ?category=pizza
    """
    category = request.GET.get('category')  # Get 'category' parameter from query
    if not category:
        return JsonResponse({"message": "Category is required", "status": "error"}, status=400)

    try:
        # Query FoodData collection to get items with matching 'foodType'
        menu_items_ref = db.collection("FoodData").where("foodType", "==", category)
        menu_items = menu_items_ref.stream()

        # Parse the documents and format the response
        data = [
            {
                "name": item.to_dict().get("foodName"),
                "price": item.to_dict().get("foodPrice"),
                "image": item.to_dict().get("foodImageUrl"),
                "description": item.to_dict().get("foodDescription", "No description available"),
            }
            for item in menu_items
        ]

        # Check if data exists
        if data:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"message": f"No items found in category '{category}'", "status": "error"}, status=404)

    except Exception as e:
        # Log and return server error
        print(f"Error fetching menu data: {str(e)}")
        return JsonResponse({"message": "Internal server error", "status": "error"}, status=500)


@api_view(['POST'])
def transcribe(request):
    if 'audio' not in request.FILES:
        return JsonResponse({'error': 'No audio file provided'}, status=400)

    # Save the uploaded audio file temporarily
    audio_file = request.FILES['audio']
    temp_audio_file = f'temp_audio_{uuid.uuid4().hex}.wav'

    try:
        with open(temp_audio_file, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # Transcribe the audio file using the Whisper model
        transcription = transcribe_audio(temp_audio_file)
        os.remove(temp_audio_file)  # Remove the temporary file after transcription

        if transcription is None:
            return JsonResponse({'error': 'Transcription failed'}, status=500)

        # Lowercase the transcription to handle cases like 'open' or 'Open'
        transcription = transcription.lower()

        if "open" in transcription:
            # Extract the category from the transcription, e.g., "open pasta"
            category = transcription.replace("open", "").strip().title()

            # Modify the request's GET parameters to include the category for fetching the menu
            request._request.GET = request._request.GET.copy()  # Clone the GET parameters
            request._request.GET['category'] = category  # Set the category as a GET parameter

            # Call the fetch_category_menu function to get the menu based on the category
            return fetch_category_menu(request._request)

        return JsonResponse({"text": transcription}, status=200)

    except Exception as e:
        if os.path.isfile(temp_audio_file):
            os.remove(temp_audio_file)  # Clean up the file in case of an error
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('userId')
    item = request.data.get('item')

    if not user_id or not item:
        return Response({'error': 'userId and item are required'}, status=status.HTTP_400_BAD_REQUEST)

    cart_ref = db.collection('carts').document(user_id)
    cart_doc = cart_ref.get()

    if cart_doc.exists:
        cart_data = cart_doc.to_dict()
        items = cart_data.get('items', [])

        # Check if the item is already in the cart
        existing_item = next((i for i in items if i['id'] == item['id']), None)
        if existing_item:
            existing_item['quantity'] += 1  # Update quantity
            cart_ref.update({'items': items})
        else:
            items.append({**item, 'quantity': 1})  # Add new item
            cart_ref.set({'items': items}, merge=True)
    else:
        # Create a new cart if it doesn't exist
        cart_ref.set({'items': [{**item, 'quantity': 1}]})

    return Response({'message': 'Item added to cart successfully!'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def upload_profile_picture(request):
    user = request.user  # Get the authenticated user
    serializer = ProfilePictureSerializer(data=request.data)

    if serializer.is_valid():
        # If the profile picture is valid, upload it to Firebase Storage and update the user's profile
        profile_picture = serializer.validated_data['profile_picture']
        image_url = serializer.update_user_profile_picture(user, profile_picture)
        return JsonResponse({"message": "Profile picture updated successfully", "profile_picture_url": image_url}, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def facebook_data_deletion(request):
    if request.method == "POST":  # Facebook may send POST or GET
        try:
            user_id = request.POST.get("user_id")  # UID of the user requesting data deletion

            if not user_id:
                return JsonResponse({"status": "error", "message": "User ID is required."}, status=400)

            # Perform the deletion logic here
            # For example, deleting from Firebase Realtime Database
            from firebase_admin import db
            ref = db.reference(f'users/{user_id}')
            ref.delete()

            # Response required by Facebook
            return JsonResponse({
                "url": "http://192.168.18.128:8000/deletion-status"  # Replace with your actual status URL
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # If it's a GET request or any invalid method, return an error
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)



# import hmac


# def generate_hmac_sha256(data, shared_secret):
#     # Sort the fields in ascending alphabetical order of the ASCII value
#     sorted_fields = sorted((key, value) for key, value in data.items() if value)
#     concatenated_string = '&'.join(f"{key}={value}" for key, value in sorted_fields)

#     # Prepend the shared secret
#     secure_string = f"{shared_secret}&{concatenated_string}"

#     # Generate HMAC SHA256 hash
#     hash_object = hmac.new(
#         shared_secret.encode('utf-8'), 
#         secure_string.encode('utf-8'), 
#         hashlib.sha256
#     )

#     return hash_object.hexdigest().upper()

# @ensure_csrf_cookie
# @csrf_protect
# def initiate_payment(request):
#     if request.method == 'POST':
#         txn_datetime = datetime.datetime.now()
#         data = {
#             "pp_Amount": "100",
#             "pp_BankID": "",
#             "pp_BillReference": "bill123",
#             "pp_CNIC": "345678",
#             "pp_Description": "Order Payment",
#             "pp_Language": "EN",
#             "pp_MerchantID": settings.JAZZCASH_MERCHANT_ID,
#             "pp_MobileNumber": "03123456789",
#             "pp_Password": settings.JAZZCASH_PASSWORD,
#             "pp_ProductID": "",
#             "pp_ReturnURL": settings.JAZZCASH_RETURN_URL,
#             "pp_SecureHash": "",
#             "pp_SubMerchantID": "",
#             "pp_TxnCurrency": "PKR",
#             "pp_TxnDateTime": txn_datetime.strftime('%Y%m%d%H%M%S'),
#             "pp_TxnExpiryDateTime": (txn_datetime + datetime.timedelta(minutes=10)).strftime('%Y%m%d%H%M%S'),
#             "pp_TxnRefNo": f"TXN{txn_datetime.strftime('%Y%m%d%H%M%S')}",
#             "pp_TxnType": "MWALLET",
#             "pp_Version": "1.1",
#             "ppmpf_1": "03122036440",
#             "ppmpf_2": "",
#             "ppmpf_3": "",
#             "ppmpf_4": "",
#             "ppmpf_5": "",
#         }

#         shared_secret = settings.JAZZCASH_INTEGRITY_KEY
#         data["pp_SecureHash"] = generate_hmac_sha256(data, shared_secret)

#         # Log sanitized data
#         data_to_log = data.copy()
#         data_to_log["pp_SecureHash"] = "REDACTED"
#         print("Data being sent to JazzCash:", data_to_log)

#         try:
#             response = requests.post(
#                 "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction",
#                 data=data
#             )
#             print("Response Status Code:", response.status_code)
#             try:
#                 response_json = response.json()
#                 print("JazzCash Response:", response_json)
#             except ValueError:
#                 return JsonResponse({"success": False, "error": "Invalid JSON response.", "raw": response.text})

#             if response.status_code == 200:
#                 return JsonResponse({"success": True, "data": response_json})
#             else:
#                 return JsonResponse({"success": False, "error": response_json})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})

#     return JsonResponse({"success": False, "error": "Invalid request method."})

# @ensure_csrf_cookie
# def get_csrf_token(request):
#     return JsonResponse({'csrfToken': get_token(request)})

@api_view(['POST'])
def create_payment_intent(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        data = request.data
        amount = int(data.get("amount", 0))  # Amount in cents

        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        # Create PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,  # Amount in cents
            currency="pkr",
            payment_method_types=["card"],
            metadata={
                "userEmail": data.get("email"),
                "userName": data.get("name"),
            },
        )

        return Response({
            "clientSecret": payment_intent.client_secret
        })

    except Exception as e:
        print(f"Stripe Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_stripe_checkout_session(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        data = request.data
        items = data.get('items', [])
        metadata = data.get('metadata', {})
        if not items or not isinstance(items, list):
            return Response({'error': 'Invalid items format. Please provide a list of items.'}, status=status.HTTP_400_BAD_REQUEST)

        line_items = []
        for item in items:
            # Validate the item format
            if not isinstance(item, dict) or 'name' not in item or 'price' not in item or 'quantity' not in item:
                return Response({'error': 'Invalid item format. Each item must contain "name", "price", and "quantity".'}, status=status.HTTP_400_BAD_REQUEST)

            line_items.append({
                'price_data': {
                    'currency': 'PKR',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(item['price'] * 100),  # converting to cents
                },
                'quantity': item['quantity'],
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url="https://d991-2407-d000-d-a006-b927-58e1-68a8-4a1d.ngrok-free.app/api/success",
            cancel_url="http://192.168.18.128:8000/cancel",
            metadata=metadata, 
        )

        return Response({'checkout_url': checkout_session.url})

    except Exception as e:
        print(f"Stripe Error: {str(e)}")  # Print error to terminal
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode('utf-8')  # Decode the raw JSON data
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        print("❌ Missing Stripe Signature")
        return JsonResponse({'error': 'Missing Stripe Signature'}, status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        print("❌ Invalid Stripe Signature:", str(e))
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        print("❌ Error parsing webhook:", str(e))
        return JsonResponse({'error': 'Webhook processing error'}, status=400)

    # ✅ Log the event for debugging
    print("🔹 Stripe Webhook Event Received:", json.dumps(event, indent=2))

    # Extract session details safely
    session = event.get('data', {}).get('object', {})
    email = session.get('customer_details', {}).get('email', "Unknown Email")
    amount = session.get('amount_total', 0) / 100  # Convert cents to PKR
    payment_intent = session.get('payment_intent')
    stripe_order_id = session.get('id')  # Unique order ID from Stripe
    currency = session.get('currency', 'PKR').upper()

    # Extract user profile data from metadata
    metadata = session.get('metadata', {})
    user_email = metadata.get('userEmail', "")
    user_name = metadata.get('userName', "")
    user_phone = metadata.get('userPhone', "")
    user_address = metadata.get('userAddress', "")
    user_id = metadata.get('userId', "")

    # Items purchased (from metadata)
    items = metadata.get('items', "[]")
    items = json.loads(items) if isinstance(items, str) else items

    # When checkout is completed, store order in Firestore
    if event['type'] == 'checkout.session.completed':
        if payment_intent:
            print(f"✅ Payment of Rs. {amount} received from {email} (Intent ID: {payment_intent})")

            # Generate a short order ID
            short_order_id = generate(size=8)  # Generates an 8-character unique ID

            # Transform data into the desired format
            order_data = {
                "orderaddress": user_address,  # Include user address
                "ordercost": amount,
                "orderdata": items,  # Include cart items
                "orderdate": firestore.SERVER_TIMESTAMP,
                "orderid": short_order_id,  # Use the short order ID
                "ordername": user_name,  # Include user name
                "orderpayment": "online",
                "orderphone": user_phone,  # Include user phone
                "orderstatus": "ontheway",
                "orderuseruid": user_id,  # Include user ID
                "paymentstatus": "paid",
            }

            # Save order details in Firestore
            db.collection("UserOrders").document(short_order_id).set(order_data)
            print(f"✅ Order successfully saved to Firestore: {short_order_id}")
        else:
            print(f"⚠️ Payment completed but no payment_intent found for {email}.")

    elif event['type'] == 'payment_intent.succeeded':
        print(f"✅ Payment Intent {payment_intent} succeeded for Rs. {amount}!")

    elif event['type'] == 'payment_intent.payment_failed':
        print(f"❌ Payment failed for {email}.")

    return JsonResponse({'status': 'success'}, status=200)
# @csrf_exempt
# @api_view(['POST'])
# def create_stripe_payment_intent(request):
#     try:
#         stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure this is set correctly
#         data = request.data
#         print("Received data from frontend:", data)
#         amount = data.get('amount')

#         if not amount or not isinstance(amount, int) or amount <= 0:
#             return Response({'error': 'Invalid amount. Amount must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

#         payment_intent = stripe.PaymentIntent.create(
#             amount=amount,
#             currency='pkr',
#             payment_method_types=['card'],
#         )
#         print(payment_intent['client_secret'])

#         return Response({'client_secret': payment_intent.client_secret}, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f"Stripe Error: {str(e)}")
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def success_view(request):
    redirect_url = "voiceorderapp://payment-success"
    
    # Manually allow the redirect
    if redirect_url.startswith("voiceorderapp://"):
        return HttpResponseRedirect(redirect_url)
    
    raise DisallowedRedirect(f"Unsafe redirect: {redirect_url}")


class JazzCashPaymentView(APIView):
    def post(self, request):
        # Extract data from request
        amount = request.data.get('amount')
        order_id = request.data.get('order_id')
        return_url = request.data.get('return_url')

        # JazzCash API URL
        jazzcash_url = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction"

        # Prepare payload
        payload = {
    "pp_Version": "1.1",
    "pp_TxnType": "MWALLET",
    "pp_Language": "EN",
    "pp_MerchantID": "MC148195",  # Your Merchant ID
    "pp_Password": "t233vzg7fz",  # Your Password
    "pp_SubMerchantID": "",
    "pp_TxnRefNo": 'T20221125153224',
    "pp_Amount": amount,
    "pp_TxnCurrency": "PKR",
    "pp_TxnDateTime": "20250202021600",  # Replace with current datetime
    "pp_BillReference": order_id,
    "pp_Description": "Payment for Order",
    "pp_ReturnURL": return_url,
    "ppmpf_1": "03122036440",  # Customer's mobile number
    "ppmpf_2": "",  # Optional
    "ppmpf_3": "",  # Optional
    "ppmpf_4": "",  # Optional
    "ppmpf_5": ""   # Optional
}
        # Generate the secure hash and add it to the payload
        payload["pp_SecureHash"] = self.generate_secure_hash(payload)

        # Send request to JazzCash
        response = requests.post(jazzcash_url, json=payload)
        response_data = response.json()

        # Log the response
        logger.info(f"JazzCash API Response: {response_data}")

        # Save transaction details to Firestore
        transaction_data = {
            'amount': amount,
            'transaction_id': response_data.get('pp_TxnRefNo'),
            'status': response_data.get('pp_ResponseMessage'),
            'created_at': firestore.SERVER_TIMESTAMP
        }
        db.collection('transactions').add(transaction_data)

        return Response(response_data, status=status.HTTP_200_OK)

    def generate_secure_hash(self, payload):
        # Sort all fields starting with 'pp_' in alphabetical order
        sorted_fields = sorted(payload.items(), key=lambda x: x[0])
        # Concatenate the sorted fields with '&' as the separator
        concatenated_string = '&'.join([f"{key}={value}" for key, value in sorted_fields if key.startswith('pp_')])
        # Prepend the Integrity Salt (Shared Secret)
        integrity_salt = "wzu8tex9us"  # Replace with your actual Integrity Salt
        message = f"{integrity_salt}&{concatenated_string}"
        # Calculate the HMAC-SHA256 hash
        key = integrity_salt.encode('utf-8')
        message_bytes = message.encode('utf-8')
        hmac_hash = hmac.new(key, message_bytes, hashlib.sha256).hexdigest()
        return hmac_hash.upper()

class JazzCashCallbackView(APIView):
    def post(self, request):
        # Handle JazzCash callback
        response_data = request.data
        transaction_id = response_data.get('pp_TxnRefNo')
        status = response_data.get('pp_ResponseMessage')

        # Update transaction status in Firestore
        transactions_ref = db.collection('transactions')
        transaction = transactions_ref.where('transaction_id', '==', transaction_id).get()
        if transaction:
            for doc in transaction:
                doc.reference.update({'status': status})

        return Response({"status": "success"}, status=status.HTTP_200_OK)

encoder = VoiceEncoder()
   
# @api_view(['POST'])
# def process_voice_samples(request):

#     user_id = request.data.get('userId', f"user_{uuid.uuid4().hex}")  
#     audio_files = request.FILES.getlist('audio_samples')

#     if not audio_files:
#         return JsonResponse({'error': 'No audio files provided'}, status=400)

#     embeddings = []

#     try:
#         for audio_file in audio_files:
#             temp_audio_file = f'temp_{uuid.uuid4().hex}.wav'
#             with open(temp_audio_file, 'wb+') as destination:
#                 for chunk in audio_file.chunks():
#                     destination.write(chunk)

#             print(f"Processing: {temp_audio_file}")  

#             try:
#                 embedding = process_audio(temp_audio_file)
#                 print("Embedding extracted successfully!")  
#             except Exception as e:
#                 print(f"Error processing audio: {str(e)}")  
#                 return JsonResponse({'error': f'Error processing audio: {str(e)}'}, status=500)

#             os.remove(temp_audio_file)  

          
#             if isinstance(embedding, np.ndarray) and embedding.size > 0:
#                 embeddings.append(embedding)
#             else:
#                 print(f"Invalid embedding for file {temp_audio_file}")  

#         print(f"Total embeddings extracted: {len(embeddings)}") 

#         if embeddings:
#             try:
#                 save_embeddings_to_firebase(user_id, embeddings)
#                 print(f"Saved to Firebase for user: {user_id}") 
#             except Exception as e:
#                 print(f"Firebase Error: {str(e)}")  
#                 return JsonResponse({'error': f'Firebase Error: {str(e)}'}, status=500)

#             return JsonResponse({"message": "Voice samples processed and saved successfully", "userId": user_id}, status=200)
#         else:
#             return JsonResponse({'error': 'Failed to process audio files'}, status=500)

#     except Exception as e:
#         print(f"Unexpected Error: {str(e)}")  
#         return JsonResponse({'error': str(e)}, status=500)

# @api_view(['POST'])
# def authenticate_voice(request):
#     user_id = request.data.get('userId')
#     audio_file = request.FILES.get('audio_sample')

#     if not audio_file:
#         return JsonResponse({'error': 'No audio file provided'}, status=400)

#     try:
#         # Process the incoming voice sample
#         temp_audio_file = f'temp_{uuid.uuid4().hex}.wav'
#         with open(temp_audio_file, 'wb+') as destination:
#             for chunk in audio_file.chunks():
#                 destination.write(chunk)
        
#         incoming_embedding = process_audio(temp_audio_file)
#         os.remove(temp_audio_file)

#         if incoming_embedding is None:
#             return JsonResponse({'error': 'Failed to process audio sample'}, status=500)

#         # Fetch the registered embedding from Firebase
#         registered_embeddings = get_registered_embedding(user_id)
        
#         if not registered_embeddings:
#             return JsonResponse({'error': 'User not registered or no embeddings found'}, status=404)

#         # Compare embeddings (assuming only one embedding is stored per user)
#         is_authenticated = False
#         for registered_embedding in registered_embeddings:
#             if compare_embeddings(registered_embedding, incoming_embedding):
#                 is_authenticated = True
#                 break

#         if is_authenticated:
#             return JsonResponse({"message": "Voice authenticated successfully"}, status=200)
#         else:
#             return JsonResponse({'error': 'Voice does not match the registered voice'}, status=403)

#     except Exception as e:
#         print(f"Error authenticating voice: {e}")
#         return JsonResponse({'error': 'Error authenticating voice'}, status=500)

def check_enrollment_status_view(request):
    user_id = request.GET.get('user_id')  # Or get from request body depending on your setup
    
    if user_id is None:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    
    enrollment_status = check_enrollment_status(user_id)
    return JsonResponse({'enrollment_status': enrollment_status})
def process_audio(file_path):

    if not os.path.isfile(file_path):

        print(f"Error: File '{file_path}' does not exist.")

        return None

    

    try:

        wav = preprocess_wav(file_path)  

        embedding = encoder.embed_utterance(wav)  

        if isinstance(embedding, np.ndarray) and embedding.size > 0:

            return embedding  

        else:

            print("Error: Embedding is empty or invalid.")

            return None

    except Exception as e:

        print(f"Error processing audio: {e}")

        return None


def get_registered_embedding(user_id):

    try:

        user_ref = db.collection("VoiceId").document(user_id)

        user_data = user_ref.get()

        if user_data.exists:

            embeddings = user_data.to_dict()

            embeddings_list = [np.array(embedding) for embedding in embeddings.values()]

            return embeddings_list

        else:

            return None

    except Exception as e:

        print(f"Error fetching registered embeddings: {e}")

        return None


def compare_embeddings(registered_embedding, incoming_embedding):

    try:

        cosine_similarity = np.dot(registered_embedding, incoming_embedding) / (np.linalg.norm(registered_embedding) * np.linalg.norm(incoming_embedding))

        threshold = 0.8  

        return cosine_similarity > threshold

    except Exception as e:

        print(f"Error comparing embeddings: {e}")

        return False


@api_view(['POST'])

def authenticate_voice(request):

    user_id = request.data.get('userId')

    audio_file = request.FILES.get('audio_sample')


    if not audio_file:

        return JsonResponse({'error': 'No audio file provided'}, status=400)


    try:

        temp_audio_file = f'temp_{uuid.uuid4().hex}.wav'

        with open(temp_audio_file, 'wb+') as destination:

            for chunk in audio_file.chunks():

                destination.write(chunk)

        

        incoming_embedding = process_audio(temp_audio_file)

        os.remove(temp_audio_file)


        if incoming_embedding is None:

            return JsonResponse({'error': 'Failed to process audio sample'}, status=500)


        registered_embeddings = get_registered_embedding(user_id)

        

        if not registered_embeddings:

            return JsonResponse({'error': 'User  not registered or no embeddings found'}, status=404)


        is_authenticated = any(compare_embeddings(registered_embedding, incoming_embedding) for registered_embedding in registered_embeddings)


        if is_authenticated:

            return JsonResponse({"message": "Voice authenticated successfully"}, status=200)

        else:

            return JsonResponse({'error': 'Voice does not match the registered voice'}, status=403)


    except Exception as e:

        print(f"Error authenticating voice: {e}")

        return JsonResponse({'error': 'Error authenticating voice'}, status=500)
    
def list_users(request):
    try:
        users = auth.list_users().iterate_all()  # Fetch all users
        user_list = [
            {"email": user.email, "uid": user.uid, "created_at": user.user_metadata.creation_timestamp}
            for user in users
        ]
        return JsonResponse({"users": user_list}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Item
from firebase_admin import firestore

db = firestore.client()

@api_view(['POST'])
def update_stock(request):
    items = request.data.get('items', [])
    for item_data in items:
        item_id = item_data.get('id')
        quantity = item_data.get('quantity')
        item = Item.objects.get(id=item_id)
        item.quantity -= quantity
        item.save()

        # Update Firestore
        db.collection('FoodData').document(str(item_id)).update({
            'quantity': item.quantity
        })

    return Response({'status': 'success'})
@api_view(['GET'])
def get_stock(request, item_id):
    item = Item.objects.get(id=item_id)
    return Response({'quantity': item.quantity})

@api_view(['POST'])
def process_voice_samples(request):

    user_id = request.data.get('userId')
    if not user_id:
        return JsonResponse({'error': 'Missing userId'}, status=400)
  
    audio_files = request.FILES.getlist('audio_samples')

    if not audio_files:
        return JsonResponse({'error': 'No audio files provided'}, status=400)

    embeddings = []

    try:
        for audio_file in audio_files:
            temp_audio_file = f'temp_{uuid.uuid4().hex}.wav'
            with open(temp_audio_file, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            print(f"Processing: {temp_audio_file}")  

            try:
                embedding = process_audio(temp_audio_file)
                print("Embedding extracted successfully!")  
            except Exception as e:
                print(f"Error processing audio: {str(e)}")  
                return JsonResponse({'error': f'Error processing audio: {str(e)}'}, status=500)

            os.remove(temp_audio_file)  

          
            if isinstance(embedding, np.ndarray) and embedding.size > 0:
                embeddings.append(embedding)
            else:
                print(f"Invalid embedding for file {temp_audio_file}")  

        print(f"Total embeddings extracted: {len(embeddings)}") 

        if embeddings:
            try:
                save_embeddings_to_firebase(user_id, embeddings)
                print(f"Saved to Firebase for user: {user_id}") 
            except Exception as e:
                print(f"Firebase Error: {str(e)}")  
                return JsonResponse({'error': f'Firebase Error: {str(e)}'}, status=500)

            return JsonResponse({"message": "Voice samples processed and saved successfully", "userId": user_id}, status=200)
        else:
            return JsonResponse({'error': 'Failed to process audio files'}, status=500)

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")  
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def verify_voice_sample(request):
    try:
        logger.info("Received verification request")

        user_id = request.data.get('userId')
        audio_file = request.FILES.get('audio_sample')

        if not user_id or not audio_file:
            logger.error("Missing parameters: userId or audio_sample")
            return JsonResponse({'error': 'Missing userId or audio_sample'}, status=400)

        temp_audio_file = f'temp_verify_{uuid.uuid4().hex}.wav'
        logger.info(f"Creating temp file: {temp_audio_file}")

        try:
            # Save uploaded audio to temp file
            with open(temp_audio_file, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            logger.info("Audio file saved, processing...")
            user_embedding = process_audio(temp_audio_file)

            if not isinstance(user_embedding, np.ndarray):
                logger.error("Invalid embedding format")
                return JsonResponse({'error': 'Failed to extract embedding'}, status=500)

            logger.info("Querying Firebase for stored embeddings...")
            doc_ref = db.collection('VoiceId').document(user_id)
            doc = doc_ref.get()

            if not doc.exists:
                logger.error(f"No embeddings found for user {user_id}")
                return JsonResponse({'error': 'No embeddings found for user'}, status=404)

            doc_data = doc.to_dict()
            stored_embedding_array = [doc_data[key] for key in sorted(doc_data.keys(), key=lambda x: int(x.split('_')[1]))]
            stored_embeddings = [np.array(e) for e in stored_embedding_array]  # Wrap in list to allow future expansion

            # Compare with stored embedding(s)
            threshold = 0.70
            match_found = any(
                cosine_similarity(user_embedding, embedding) >= threshold
                for embedding in stored_embeddings
            )

            logger.info(f"Verification result: {match_found}")
            return JsonResponse({'matched': match_found}, status=200)

        except Exception as e:
            logger.exception("Error during verification process")
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            if os.path.exists(temp_audio_file):
                try:
                    os.remove(temp_audio_file)
                except Exception as e:
                    logger.warning(f"Could not remove temp file: {str(e)}")

    except Exception as e:
        logger.exception("Unhandled exception in verify_voice_sample")
        return JsonResponse({'error': 'Internal server error'}, status=500)



def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))