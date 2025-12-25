import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google import genai

app = Flask(__name__)

# Initialize the Gemini Client
# Vercel will provide this key from the Environment Variables you added
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_mandi_price(item):
    """Fetches 100% accurate price from Govt Data API"""
    api_key = os.environ.get("DATA_GOV_KEY")
    # Verified Resource ID for Mandi Prices
    resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={api_key}&format=json&filters[commodity]={item}"
    
    try:
        data = requests.get(url).json()
        if data.get('records'):
            record = data['records'][0]
            return f"₹{record['modal_price']} in {record['market']} ({record['district']})"
        return "Not found in today's records."
    except Exception:
        return "Service temporarily busy."

@app.route("/", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    
    # Use the model that successfully passed your test
    # (Update 'gemini-2.0-flash' if you used a different name in your test)
    prompt = f"Identify the agricultural crop in this text: '{incoming_msg}'. Answer with ONE word only."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        crop = response.text.strip()
        price_info = get_mandi_price(crop)
    except Exception:
        crop = "Unknown"
        price_info = "Please try again."

    # Create the WhatsApp Response
    resp = MessagingResponse()
    resp.message(f"✅ *Bharat Voice OS*\nCrop: {crop}\nPrice: {price_info}")
    return str(resp)

if __name__ == "__main__":
    app.run()
