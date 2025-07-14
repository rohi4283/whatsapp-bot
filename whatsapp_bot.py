from flask import Flask, request
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

def get_phonenumbers_data(number: str):
    try:
        parsed = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Invalid phone number format."}

        return {
            "✅ Valid": "Yes",
            "📞 Formatted": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "🗺 Region": geocoder.description_for_number(parsed, "en"),
            "📡 Carrier": carrier.name_for_number(parsed, "en"),
            "🕐 Timezones": ", ".join(timezone.time_zones_for_number(parsed))
        }
    except Exception as e:
        return {"error": f"Parse error: {e}"}

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip()
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg.startswith('+'):
        details = get_phonenumbers_data(incoming_msg)
        if "error" in details:
            msg.body(f"❌ Error: {details['error']}")
        else:
            result_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
            msg.body(f"📋 Phone Info:\n{result_text}")
    else:
        msg.body("👋 Send a phone number starting with `+` (e.g. +254712345678) to get details.")

    return str(response)

@app.route("/", methods=['GET'])
def home():
    return "✅ WhatsApp bot is live! Use the /whatsapp endpoint via POST."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

