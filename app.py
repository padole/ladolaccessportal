import os
from myapp import app

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 8082))
    app.run(debug=debug, port=port)
