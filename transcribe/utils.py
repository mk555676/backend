import hashlib

def generate_signature(data, integrity_key):
    # Create a string to hash
    raw_string = f"{data['pp_MerchantID']}|{data['pp_Password']}|{data['pp_TxnRefNo']}|{data['pp_Amount']}|{data['pp_TxnCurrency']}|{data['pp_TxnDateTime']}|{data['pp_Language']}|{data['pp_BillReference']}|{data['pp_Description']}|{integrity_key}"
    
    # Log the raw string for debugging
    print("Raw string for secure hash:", raw_string)
    
    # Generate the secure hash
    signature = hashlib.sha256(raw_string.encode()).hexdigest()
    return signature 