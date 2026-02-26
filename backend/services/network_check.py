from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def check_server(url):
    try:
        response = requests.get(url, timeout=5)

        return {
            "reachable": True,
            "status_code": response.status_code
        }

    except requests.exceptions.RequestException:
        return {
            "reachable": False
        }


@app.route('/validate-servers', methods=['POST'])
def validate_servers():
    data = request.get_json()

    if not data or 'auth_url' not in data or 'jwks_url' not in data:
        return jsonify({
            "message": "Please provide both Authentication Server URL and JWKS Server URL."
        }), 400

    auth_url = data['auth_url']
    jwks_url = data['jwks_url']

    auth_result = check_server(auth_url)
    jwks_result = check_server(jwks_url)

    # BOTH reachable
    if auth_result["reachable"] and jwks_result["reachable"]:
        return jsonify({
            "message": "Both the Authentication Server and JWKS Server are reachable. Network connectivity is successful.",
            "auth_server": f"Reachable (HTTP {auth_result['status_code']})",
            "jwks_server": f"Reachable (HTTP {jwks_result['status_code']})"
        })

    # BOTH not reachable
    if not auth_result["reachable"] and not jwks_result["reachable"]:
        return jsonify({
            "message": "Neither server could be reached. Network connectivity failed.",
            "auth_server": "Not Reachable",
            "jwks_server": "Not Reachable"
        })

    # Only auth fails
    if not auth_result["reachable"]:
        return jsonify({
            "message": "The Authentication Server could not be reached. Network connectivity failed.",
            "auth_server": "Not Reachable",
            "jwks_server": f"Reachable (HTTP {jwks_result['status_code']})"
        })

    # Only jwks fails
    if not jwks_result["reachable"]:
        return jsonify({
            "message": "The JWKS Server could not be reached. Network connectivity failed.",
            "auth_server": f"Reachable (HTTP {auth_result['status_code']})",
            "jwks_server": "Not Reachable"
        })


if __name__ == '__main__':
    app.run(debug=True)