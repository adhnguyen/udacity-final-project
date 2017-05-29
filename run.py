from app import app

# Set the secret key
app.secret_key = 'P\xb1\x97\ry(\xb4\xcc\x10\xd2\x9d\xc7\xc1\xaf2\x8f,\xac*\x98H\xdbi\xe7'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)