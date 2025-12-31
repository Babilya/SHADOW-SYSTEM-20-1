import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

logger = logging.getLogger(__name__)


class AlertChannel(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ChannelConfig:
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailConfig:
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    use_tls: bool = True


@dataclass
class WebhookConfig:
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    include_signature: bool = True
    secret_key: Optional[str] = None
    timeout: int = 30


@dataclass
class EnhancedAlert:
    id: str
    title: str
    message: str
    severity: AlertSeverity
    channels: List[AlertChannel]
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    delivered_to: List[str] = field(default_factory=list)
    failed_channels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "channels": [c.value for c in self.channels],
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "delivered_to": self.delivered_to,
            "failed_channels": self.failed_channels
        }


class EnhancedAlertSystem:
    SEVERITY_COLORS = {
        AlertSeverity.INFO: "#3498db",
        AlertSeverity.WARNING: "#f39c12",
        AlertSeverity.ERROR: "#e74c3c",
        AlertSeverity.CRITICAL: "#9b59b6"
    }
    
    SEVERITY_ICONS = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.ERROR: "❌",
        AlertSeverity.CRITICAL: "🚨"
    }
    
    def __init__(self):
        self.alerts: Dict[str, EnhancedAlert] = {}
        self.channel_configs: Dict[AlertChannel, ChannelConfig] = {}
        self.subscribers: Dict[int, Dict[AlertChannel, Any]] = {}
        self.telegram_callback: Optional[Callable] = None
        self.email_config: Optional[EmailConfig] = None
        self.webhooks: List[WebhookConfig] = []
        self._counter = 0
        self.stats = {
            "total_sent": 0,
            "telegram_sent": 0,
            "email_sent": 0,
            "webhook_sent": 0,
            "failed": 0
        }
    
    def configure_telegram(self, callback: Callable):
        self.telegram_callback = callback
        self.channel_configs[AlertChannel.TELEGRAM] = ChannelConfig(enabled=True)
        logger.info("Telegram channel configured")
    
    def configure_email(self, config: EmailConfig):
        self.email_config = config
        self.channel_configs[AlertChannel.EMAIL] = ChannelConfig(
            enabled=True,
            settings={"host": config.smtp_host, "port": config.smtp_port}
        )
        logger.info(f"Email channel configured: {config.smtp_host}")
    
    def add_webhook(self, config: WebhookConfig):
        self.webhooks.append(config)
        self.channel_configs[AlertChannel.WEBHOOK] = ChannelConfig(
            enabled=True,
            settings={"webhooks_count": len(self.webhooks)}
        )
        logger.info(f"Webhook added: {config.url}")
    
    def subscribe_user(
        self,
        user_id: int,
        channels: Dict[AlertChannel, Any]
    ):
        self.subscribers[user_id] = channels
        logger.info(f"User {user_id} subscribed to channels: {list(channels.keys())}")
    
    def _generate_id(self) -> str:
        self._counter += 1
        return f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._counter:04d}"
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        channels: Optional[List[AlertChannel]] = None,
        target_users: Optional[List[int]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> EnhancedAlert:
        if channels is None:
            channels = [AlertChannel.TELEGRAM]
        
        alert = EnhancedAlert(
            id=self._generate_id(),
            title=title,
            message=message,
            severity=severity,
            channels=channels,
            data=data or {}
        )
        
        self.alerts[alert.id] = alert
        
        tasks = []
        
        if AlertChannel.TELEGRAM in channels:
            tasks.append(self._send_telegram(alert, target_users))
        
        if AlertChannel.EMAIL in channels:
            tasks.append(self._send_email(alert, target_users))
        
        if AlertChannel.WEBHOOK in channels:
            tasks.append(self._send_webhooks(alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats["total_sent"] += 1
        logger.info(f"Alert sent: {alert.id} via {[c.value for c in channels]}")
        
        return alert
    
    async def _send_telegram(
        self,
        alert: EnhancedAlert,
        target_users: Optional[List[int]] = None
    ):
        if not self.telegram_callback:
            alert.failed_channels.append("telegram")
            return
        
        users = target_users or [
            uid for uid, channels in self.subscribers.items()
            if AlertChannel.TELEGRAM in channels
        ]
        
        icon = self.SEVERITY_ICONS.get(alert.severity, "📢")
        formatted_message = f"""{icon} <b>{alert.title}</b>

{alert.message}

<i>ID: {alert.id}</i>
<i>Час: {alert.created_at.strftime('%d.%m.%Y %H:%M:%S')}</i>"""
        
        for user_id in users:
            try:
                await self.telegram_callback(user_id, formatted_message)
                alert.delivered_to.append(f"telegram:{user_id}")
                self.stats["telegram_sent"] += 1
            except Exception as e:
                logger.error(f"Failed to send Telegram alert to {user_id}: {e}")
                self.stats["failed"] += 1
    
    async def _send_email(
        self,
        alert: EnhancedAlert,
        target_users: Optional[List[int]] = None
    ):
        if not self.email_config:
            alert.failed_channels.append("email")
            return
        
        recipients = []
        if target_users:
            for uid in target_users:
                user_channels = self.subscribers.get(uid, {})
                email = user_channels.get(AlertChannel.EMAIL)
                if email:
                    recipients.append(email)
        
        if not recipients:
            return
        
        color = self.SEVERITY_COLORS.get(alert.severity, "#333")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background: #f9f9f9; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
        .severity {{ display: inline-block; padding: 5px 10px; border-radius: 4px; background: {color}; color: white; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SHADOW SYSTEM Alert</h1>
        </div>
        <div class="content">
            <span class="severity">{alert.severity.value.upper()}</span>
            <h2>{alert.title}</h2>
            <p>{alert.message}</p>
            <hr>
            <p><small>Alert ID: {alert.id}<br>Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        <div class="footer">
            SHADOW SYSTEM iO v2.0 - Automated Alert System
        </div>
    </div>
</body>
</html>
"""
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.title}"
            msg["From"] = self.email_config.from_email
            msg["To"] = ", ".join(recipients)
            
            msg.attach(MIMEText(alert.message, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.email_config.smtp_host, self.email_config.smtp_port) as server:
                if self.email_config.use_tls:
                    server.starttls(context=context)
                server.login(self.email_config.username, self.email_config.password)
                server.sendmail(
                    self.email_config.from_email,
                    recipients,
                    msg.as_string()
                )
            
            for email in recipients:
                alert.delivered_to.append(f"email:{email}")
                self.stats["email_sent"] += 1
            
            logger.info(f"Email alert sent to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            alert.failed_channels.append("email")
            self.stats["failed"] += 1
    
    async def _send_webhooks(self, alert: EnhancedAlert):
        if not self.webhooks:
            alert.failed_channels.append("webhook")
            return
        
        payload = {
            "alert_id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "timestamp": alert.created_at.isoformat(),
            "data": alert.data,
            "source": "shadow_system"
        }
        
        async with aiohttp.ClientSession() as session:
            for webhook in self.webhooks:
                try:
                    headers = {"Content-Type": "application/json"}
                    headers.update(webhook.headers)
                    
                    if webhook.include_signature and webhook.secret_key:
                        import hmac
                        import hashlib
                        signature = hmac.new(
                            webhook.secret_key.encode(),
                            json.dumps(payload).encode(),
                            hashlib.sha256
                        ).hexdigest()
                        headers["X-Signature"] = signature
                    
                    async with session.request(
                        webhook.method,
                        webhook.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=webhook.timeout)
                    ) as response:
                        if response.status in (200, 201, 202, 204):
                            alert.delivered_to.append(f"webhook:{webhook.url}")
                            self.stats["webhook_sent"] += 1
                            logger.info(f"Webhook delivered: {webhook.url}")
                        else:
                            logger.error(f"Webhook failed: {webhook.url} - Status {response.status}")
                            self.stats["failed"] += 1
                            
                except asyncio.TimeoutError:
                    logger.error(f"Webhook timeout: {webhook.url}")
                    self.stats["failed"] += 1
                except Exception as e:
                    logger.error(f"Webhook error: {webhook.url} - {e}")
                    self.stats["failed"] += 1
    
    async def send_multi_channel(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        data: Optional[Dict[str, Any]] = None
    ) -> EnhancedAlert:
        channels = [
            channel for channel, config in self.channel_configs.items()
            if config.enabled
        ]
        
        return await self.send_alert(
            title=title,
            message=message,
            severity=severity,
            channels=channels,
            data=data
        )
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "channels_configured": [c.value for c, cfg in self.channel_configs.items() if cfg.enabled],
            "subscribers_count": len(self.subscribers),
            "webhooks_count": len(self.webhooks),
            "alerts_count": len(self.alerts)
        }
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        sorted_alerts = sorted(
            self.alerts.values(),
            key=lambda a: a.created_at,
            reverse=True
        )[:limit]
        
        return [a.to_dict() for a in sorted_alerts]


enhanced_alert_system = EnhancedAlertSystem()
