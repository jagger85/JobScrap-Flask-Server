from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middlewares import user_or_admin_required
from constants import environment
from scrappers import kalibrr_v2 as kalibrr_client
import jwt
from scrappers import kalibrr_v2

kalibrr_bp = Blueprint("kalibrr", __name__)

@kalibrr_bp.route("/api/kalibrr", methods=["POST"])
@jwt_required()
def request_listings():
    try:
        #Retrieve the user from the jwt token
        token = request.headers.get("Authorization")
        user = jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])["username"]

        #Parse JSON data
        data = request.get_json(force=True)

        client = kalibrr_client(data["days"],data["keywords"])

        job_listings = client.start()

        print(job_listings)
            
        return jsonify({
        'status': 'ok',
        'message': 'Lol is working'
    }), 200

    except Exception as e:

        return jsonify({"error": f"An unexpected error occurred   {e}"})