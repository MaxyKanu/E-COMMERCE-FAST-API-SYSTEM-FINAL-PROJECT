"""
Email Notification Utilities
Demonstrates async/await requirement with simulated email sending
In production, integrate with real email service (SendGrid, Mailgun, etc.)
"""

import asyncio
from typing import Optional


async def send_email(to: str, subject: str, body: str) -> None:
    """
    Simulate sending an email asynchronously
    Uses asyncio.sleep(1) to simulate network delay
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
    """
    # Simulate email sending delay (1 second)
    await asyncio.sleep(1)
    
    # Print email details to console (in production, this would be real email)
    print(f"\n{'='*50}")
    print(f"📧 EMAIL SENT SUCCESSFULLY")
    print(f"{'='*50}")
    print(f"To:      {to}")
    print(f"Subject: {subject}")
    print(f"Body:    {body}")
    print(f"{'='*50}\n")


async def send_order_confirmation(order_id: int, user_email: str) -> None:
    """
    Send order confirmation email after successful order placement
    This function satisfies the async/await requirement
    
    Called from orders router after creating an order:
        await send_order_confirmation(order.id, current_user.email)
    
    Args:
        order_id: The ID of the created order
        user_email: Email of the user who placed the order
    """
    subject = f"Order #{order_id} Confirmed! 🎉"
    body = (
        f"Thank you for your order!\n\n"
        f"Your order #{order_id} has been received and is being processed.\n"
        f"We will notify you when your order ships.\n\n"
        f"Thank you for shopping with us!\n"
        f"- E-Commerce Inventory Team\n"
        f"  Supporting Sierra Leone Small Businesses 🇸🇱"
    )
    
    await send_email(to=user_email, subject=subject, body=body)