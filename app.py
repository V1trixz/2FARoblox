from flask import Flask, request, jsonify
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)

@app.route('/gerar', methods=['GET'])
def gerar():
    nome = request.args.get('name', 'Player')
    issuer = request.args.get('issuer', 'MeuJogo')
    
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=nome, issuer_name=issuer)
    
    # Gera QR como base64
    qr = qrcode.make(uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return jsonify({
        "secret": secret,
        "uri": uri,
        "qr_base64": qr_base64
    })

@app.route('/validar', methods=['POST'])
def validar():
    data = request.get_json()
    secret = data.get('secret')
    code = data.get('code')
    
    if not secret or not code:
        return jsonify({"valid": False, "erro": "Dados ausentes"}), 400
    
    try:
        totp = pyotp.TOTP(secret)
        valid = totp.verify(code, valid_window=1)
        return jsonify({"valid": valid})
    except Exception as e:
        return jsonify({"valid": False, "erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
