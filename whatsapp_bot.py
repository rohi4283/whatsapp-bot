from flask import Flask, request
import phonenumbers
import requests
from phonenumbers import geocoder, carrier, timezone
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "YOUR_NUMVERIFY_API_KEY")  # use .env or render env vars

def get_numverify_data(number: str):
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}&format=1"
    response = requests.get(url)
    data = response.json()

    if not data.get("valid"):
        return {"error": "Invalid number or API quota exceeded."}

    return {
        "📍 Location": data.get("location", "N/A"),
        "🌍 Country": data.get("country_name", "N/A"),
        "🌐 Country Code": data.get("country_code", "N/A"),
        "📡 Carrier": data.get("carrier", "N/A"),
        "📞 Line Type": data.get("line_type", "N/A"),
    }

def get_phonenumbers_data(number: str):
    try:
        parsed = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Invalid phone number format."}

        return {
            "✅ Valid": "Yes",
            "📞 Formatted": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "🗺 Region (lib)": geocoder.description_for_number(parsed, "en"),
            "📡 Carrier (lib)": carrier.name_for_number(parsed, "en"),
            "🕐 Timezones": ", ".join(timezone.time_zones_for_number(parsed))
        }
    except Exception as e:
        return {"error": f"Parse error: {e}"}

def get_number_info(number: str):
    result = {}
    result.update(get_phonenumbers_data(number))
    result.update(get_numverify_data(number))
    return result

@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp bot is live!"

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    incoming_msg = reques_
