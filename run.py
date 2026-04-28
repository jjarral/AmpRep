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
    print('Login: admin / admin123')
    # Use socketio.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)