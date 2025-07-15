from flask import Flask, request
import phonenumbers
import requests
from phonenumbers import geocoder, carrier, timezone
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# API keys from environment
NUMVERIFY_API_KEY = os.environ.get("f4ddf206a158a144437617bdf02320b0")
NUMLOOKUP_API_KEY = os.environ.get("num_live_tjReMv76QQpxH05ZjYxuXHem6SfjvrStnLw0UTAq")

# Local phone lib
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

# Numverify API
def get_numverify_data(number: str):
    if not NUMVERIFY_API_KEY:
        return {"error": "Numverify API key missing."}
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}&format=1"
    try:
        response = requests.get(url)
        data = response.json()
        if not data.get("valid"):
            return {"error": "Numverify: Invalid number or quota exceeded."}
        return {
            "🌍 Country": data.get("country_name", "N/A"),
            "🌐 Country Code": data.get("country_code", "N/A"),
            "📍 Location (API)": data.get("location", "N/A"),
            "📡 Carrier (API)": data.get("carrier", "N/A"),
            "📞 Line Type": data.get("line_type", "N/A"),
        }
    except Exception as e:
        return {"error": f"Numverify error: {e}"}

# Numlookup API
def get_numlookup_data(number: str):
    if not NUMLOOKUP_API_KEY:
        return {"error": "Numlookup API key missing."}
    url = f"https://api.numlookupapi.com/v1/validate/{number}?apikey={NUMLOOKUP_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if not data.get("valid", False):
            return {"error": "Numlookup: Invalid number or quota exceeded."}
        return {
            "🧍 Name": data.get("name", "Unknown"),
            "📞 Local Format": data.get("local_format", "N/A"),
            "🌍 Country": data.get("country", "N/A"),
            "🟢 Valid": str(data.get("valid", "N/A")),
        }
    except Exception as e:
        return {"error": f"Numlookup error: {e}"}

# Combine all
def get_number_info(number: str):
    result = {}
    errors = []

    for fetcher in [get_phonenumbers_data, get_numverify_data, get_numlookup_data]:
        data = fetcher(number)
        if "error" in data:
            errors.append(data["error"])
        else:
            result.update(data)

    if errors and not result:
        return {"error": "; ".join(errors)}

    return result

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "").strip()
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg.startswith("+"):
        details = get_number_info(incoming_msg)
        if "error" in details:
            msg.body(f"❌ One or more errors:\n{details['error']}")
        else:
            result_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
            msg.body(f"📋 Phone Info:\n{result_text}")
    else:
        msg.body("👋 Send a phone number starting with `+` (e.g. +254712345678) to get details.")

    return str(response)

@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp bot is live! Use the /whatsapp endpoint via POST."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
