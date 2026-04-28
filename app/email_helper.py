from flask import current_app
from flask_mail import Message
from app import mail

def send_email(subject, recipients, body, html=None):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=body,
            html=html
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_order_confirmation(order, customer_email):
    """Send order confirmation email"""
    if not customer_email or customer_email == 'N/A':
        return False
    
    subject = f'Order Confirmation - {order.order_number}'
    
    body = f"""
    Dear {order.customer_name_snapshot},
    
    Thank you for your order!
    
    Order Details:
    --------------
    Order Number: {order.order_number}
    Order Date: {order.created_at.strftime('%Y-%m-%d') if order.created_at else 'N/A'}
    Total Amount: PKR {order.total_amount:.2f}
    Payment Status: {order.payment_status.title()}
    
    Items:
    """
    
    for item in order.order_items:
        body += f"\n- {item.product.name if item.product else 'N/A'} x {item.quantity} @ PKR {item.unit_price:.2f}"
    
    body += f"""
    
    Delivery Address:
    -----------------
    {order.customer_business_snapshot or 'N/A'}
    {order.customer_phone_snapshot or 'N/A'}
    
    We will notify you once your order is shipped.
    
    Best regards,
    Ampoulex Team
    Malik Arshad Farmhouse, Malik Akram Street
    Darbar-e-Kareemi Stop, G.T. Road
    Wah Cantt, The. Taxila, Dist. RWP, Punjab, Pakistan
    Tel: 0340-5336238 | 0331-9980908
    Email: info@ampoulex.com.com
    """
    
    return send_email(subject, customer_email, body)

def send_payment_receipt(order, customer_email):
    """Send payment receipt email"""
    if not customer_email or customer_email == 'N/A':
        return False
    
    subject = f'Payment Receipt - {order.order_number}'
    
    body = f"""
    Dear {order.customer_name_snapshot},
    
    We have received your payment. Thank you!
    
    Payment Details:
    ----------------
    Order Number: {order.order_number}
    Amount Paid: PKR {order.paid_amount:.2f}
    Payment Date: {order.payment_date.strftime('%Y-%m-%d') if order.payment_date else 'N/A'}
    Payment Method: {order.payment_method.title() if order.payment_method else 'N/A'}
    
    Your order is being processed and will be shipped soon.
    
    Best regards,
    Ampoulex Team
    """
    
    return send_email(subject, customer_email, body)

def send_low_stock_alert(product, admin_email):
    """Send low stock alert to admin"""
    subject = f'Low Stock Alert - {product.name}'
    
    body = f"""
    Dear Admin,
    
    The following product is running low on stock:
    
    Product: {product.name}
    Color: {product.color}
    Current Stock: {product.stock}
    Reorder Level: 10,000
    
    Please arrange for restocking immediately.
    
    Best regards,
    Ampoulex 
    """
    
    return send_email(subject, admin_email, body)

def send_po_to_supplier(purchase_order, supplier_email):
    """Send purchase order to supplier"""
    if not supplier_email:
        return False
    
    subject = f'Purchase Order - {purchase_order.po_number}'
    
    body = f"""
    Dear Supplier,
    
    Please find below our purchase order:
    
    PO Number: {purchase_order.po_number}
    Order Date: {purchase_order.order_date.strftime('%Y-%m-%d') if purchase_order.order_date else 'N/A'}
    Expected Delivery: {purchase_order.expected_date.strftime('%Y-%m-%d') if purchase_order.expected_date else 'N/A'}
    
    Items:
    """
    
    for item in purchase_order.items:
        body += f"\n- {item.material.name} - Qty: {item.quantity_ordered} {item.material.unit} @ PKR {item.unit_price:.2f}"
    
    body += f"""
    
    Total Amount: PKR {purchase_order.grand_total:.2f}
    
    Please confirm receipt of this order.
    
    Best regards,
    Ampoulex Procurement Team
    """
    
    return send_email(subject, supplier_email, body)

def send_production_complete_notification(batch, admin_email):
    """Send production batch completion notification"""
    subject = f'Production Complete - {batch.batch_number}'
    
    body = f"""
    Dear Team,
    
    Production batch has been completed:
    
    Batch Number: {batch.batch_number}
    Product: {batch.product.name if batch.product else 'N/A'}
    Planned Quantity: {batch.planned_quantity}
    Actual Quantity: {batch.actual_quantity or 'N/A'}
    Yield: {batch.yield_percentage:.1f}% if batch.yield_percentage else 'N/A'}
    
    Best regards,
    Ampoulex 
    """
    
    return send_email(subject, admin_email, body)