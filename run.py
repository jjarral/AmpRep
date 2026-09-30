from app import create_app, db, socketio
from app.models import User, Product, Customer, Inquiry, Order, Employee, Expense

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Customer': Customer,
        'Inquiry': Inquiry,
        'Order': Order,
        'Employee': Employee,
        'Expense': Expense
    }

if __name__ == '__main__':
    print('Starting Ampoulex with real-time updates...')
    print('URL: http://localhost:5000')
    print('Set INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_EMAIL, and INITIAL_ADMIN_PASSWORD for the first local startup.')
    # Use socketio.run for WebSocket support
    # use_reloader=False to avoid issues with stat reloader in some environments
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
