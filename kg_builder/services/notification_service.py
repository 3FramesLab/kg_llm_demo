"""
Notification Service
Handles email notifications for KPI schedule executions
"""

import os
import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import pyodbc

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications about KPI schedule executions"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_email = os.getenv('NOTIFICATION_FROM_EMAIL', 'kpi-scheduler@company.com')
        
        logger.info(f"Notification service configured with SMTP server: {self.smtp_server}:{self.smtp_port}")
    
    def _get_connection(self):
        """Get database connection"""
        return pyodbc.connect(self.connection_string)
    
    def send_execution_notification(self, execution_data: Dict[str, Any], notification_type: str = 'failure'):
        """
        Send notification about KPI execution
        
        Args:
            execution_data: Execution record data
            notification_type: 'success', 'failure', 'retry'
        """
        try:
            # Get notification preferences for the schedule
            notification_configs = self._get_notification_configs(execution_data['schedule_id'])
            
            if not notification_configs:
                logger.info(f"No notification configs found for schedule {execution_data['schedule_id']}")
                return
            
            # Filter configs based on notification type
            relevant_configs = []
            for config in notification_configs:
                config_data = json.loads(config['notification_config'])
                
                if notification_type == 'failure' and config_data.get('on_failure', True):
                    relevant_configs.append(config)
                elif notification_type == 'success' and config_data.get('on_success', False):
                    relevant_configs.append(config)
                elif notification_type == 'retry' and config_data.get('on_retry', True):
                    relevant_configs.append(config)
            
            if not relevant_configs:
                logger.info(f"No relevant notification configs for {notification_type} on schedule {execution_data['schedule_id']}")
                return
            
            # Send notifications
            for config in relevant_configs:
                if config['notification_type'] == 'email':
                    self._send_email_notification(execution_data, config, notification_type)
                # Add other notification types (webhook, Slack, etc.) here
            
        except Exception as e:
            logger.error(f"❌ Failed to send execution notification: {e}")
    
    def _get_notification_configs(self, schedule_id: int) -> List[Dict[str, Any]]:
        """Get notification configurations for a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT id, notification_type, notification_config, is_active
                FROM kpi_schedule_notifications
                WHERE schedule_id = ? AND is_active = 1
            """
            
            cursor.execute(query, (schedule_id,))
            rows = cursor.fetchall()
            
            configs = []
            for row in rows:
                config = {
                    'id': row[0],
                    'notification_type': row[1],
                    'notification_config': row[2],
                    'is_active': bool(row[3])
                }
                configs.append(config)
            
            return configs
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification configs for schedule {schedule_id}: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def _send_email_notification(self, execution_data: Dict[str, Any], config: Dict[str, Any], notification_type: str):
        """Send email notification"""
        try:
            config_data = json.loads(config['notification_config'])
            recipient_email = config_data.get('email')
            
            if not recipient_email:
                logger.warning(f"No email address in notification config {config['id']}")
                return
            
            # Create email content
            subject, body = self._create_email_content(execution_data, notification_type)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            if self.smtp_username and self.smtp_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.smtp_use_tls:
                        server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # Send without authentication (for local testing)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.send_message(msg)
            
            logger.info(f"✓ Sent {notification_type} email notification to {recipient_email}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")
    
    def _create_email_content(self, execution_data: Dict[str, Any], notification_type: str) -> tuple:
        """Create email subject and body"""
        
        kpi_name = execution_data.get('kpi_name', f"KPI {execution_data.get('kpi_id')}")
        schedule_name = execution_data.get('schedule_name', f"Schedule {execution_data.get('schedule_id')}")
        
        if notification_type == 'failure':
            subject = f"🚨 KPI Execution Failed: {kpi_name}"
            status_emoji = "❌"
            status_color = "#dc3545"
            status_text = "FAILED"
        elif notification_type == 'success':
            subject = f"✅ KPI Execution Successful: {kpi_name}"
            status_emoji = "✅"
            status_color = "#28a745"
            status_text = "SUCCESS"
        elif notification_type == 'retry':
            subject = f"🔄 KPI Execution Retry: {kpi_name}"
            status_emoji = "🔄"
            status_color = "#ffc107"
            status_text = "RETRYING"
        else:
            subject = f"📊 KPI Execution Update: {kpi_name}"
            status_emoji = "📊"
            status_color = "#6c757d"
            status_text = "UPDATE"
        
        # Create HTML email body
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .status {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .detail-row {{ margin: 8px 0; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; color: #6c757d; font-size: 12px; }}
                .error-message {{ background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_emoji} KPI Execution {status_text}</h1>
                </div>
                
                <div class="content">
                    <div class="status">
                        Status: <span style="color: {status_color};">{status_text}</span>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">KPI Name:</span>
                            <span class="value">{kpi_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Schedule:</span>
                            <span class="value">{schedule_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Scheduled Time:</span>
                            <span class="value">{execution_data.get('scheduled_time', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Execution Time:</span>
                            <span class="value">{execution_data.get('actual_start_time', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Retry Count:</span>
                            <span class="value">{execution_data.get('retry_count', 0)}</span>
                        </div>
                    </div>
                    
                    {f'<div class="error-message"><strong>Error:</strong> {execution_data.get("error_message", "")}</div>' if execution_data.get('error_message') else ''}
                    
                    <p>This is an automated notification from the KPI Scheduling System.</p>
                </div>
                
                <div class="footer">
                    <p>KPI Scheduling System | Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, body
