from app import create_app

app = create_app()
application = app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)
