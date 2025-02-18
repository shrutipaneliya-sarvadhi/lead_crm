import frappe
from frappe.utils import today
from frappe.core.doctype.communication.email import make

def send_followup_notifications():
    """Send email notifications for tasks linked to leads with today's follow-up date."""
    
    # Get leads where Next Follow-Up Date is today
    leads = frappe.get_all(
        "Lead",
        filters={"custom_followup_date": today()},
        fields=["name", "first_name"]
    )

    if not leads:
        return  # No leads to process

    lead_names = [lead["name"] for lead in leads]

    # Get tasks linked to these leads
    tasks = frappe.get_all(
        "Task",
        filters={"custom_lead": ["in", lead_names]},
        fields=["name", "subject", "custom_lead", "custom_sales_team"]
    )

    for task in tasks:
        # Get email of the assigned user
        user_email = frappe.db.get_value("Sales Person", task["custom_sales_team"], "custom_email")

        if user_email:
            send_email_notification(user_email, task["subject"], task["custom_lead"])

def send_email_notification(user_email, task_subject, lead_name):
    """Send an email notification to the sales user."""
    
    subject = f"Follow-Up Reminder: {task_subject}"
    message = f"A follow-up task related to Lead {lead_name} is due today. Please take action."

    make(
        recipients=[user_email],
        subject=subject,
        content=message,
        send_email=True,
    )
    frappe.enqueue("frappe.email.queue.flush")