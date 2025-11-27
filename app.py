from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Transport Kinshasa</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #2c5aa0; }
        </style>
    </head>
    <body>
        <h1>íº— Transport Kinshasa</h1>
        <p>âœ… Service opÃ©rationnel</p>
        <p>Rond-Point Victoire â†’ Gare Centrale</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
