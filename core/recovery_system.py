"""
RecoverySystem - Система відновлення ботнету для SHADOW SYSTEM iO v2.0
Автовідновлення, ротація проксі, резервне копіювання
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import json

logger = logging.getLogger(__name__)


class RecoverySystem:
    """
    Система відновлення ботнету:
    - Автоматичне відновлення після падіння
    - Ротація проксі
    - Резервні копії сесій
    - Failover механізми
    """
    
    def __init__(self, botnet_manager=None, encryptor=None):
        self.manager = botnet_manager
        self.encryptor = encryptor
        self.proxy_pool: List[Dict] = []
        self.backup_storage: Dict[str, List[dict]] = {}
        self.recovery_attempts: Dict[str, int] = {}
        self.max_recovery_attempts = 5
        self.recovery_cooldown = 300
        
        self.settings = {
            'auto_backup_interval': 43200,
            'max_backups_per_bot': 5,
            'proxy_rotation_on_failure': True,
            'session_refresh_interval': 86400,
        }
    
    async def auto_recover_bot(self, bot_id: str) -> bool:
        """Автоматичне відновлення бота"""
        if not self.manager:
            logger.error("BotnetManager not configured")
            return False
        
        if self._is_in_cooldown(bot_id):
            logger.info(f"Bot {bot_id} in recovery cooldown")
            return False
        
        self.recovery_attempts[bot_id] = self.recovery_attempts.get(bot_id, 0) + 1
        
        if self.recovery_attempts[bot_id] > self.max_recovery_attempts:
            logger.warning(f"Max recovery attempts reached for {bot_id}")
            return False
        
        logger.info(f"🔄 Спроба відновлення бота {bot_id} (attempt {self.recovery_attempts[bot_id]})")
        
        try:
            if await self._try_reconnect(bot_id):
                logger.info(f"✅ Бот {bot_id} відновлено через перепідключення")
                self._reset_recovery_attempts(bot_id)
                return True
            
            if self.settings['proxy_rotation_on_failure']:
                if await self._rotate_proxy_and_retry(bot_id):
                    logger.info(f"✅ Бот {bot_id} відновлено з новим проксі")
                    self._reset_recovery_attempts(bot_id)
                    return True
            
            if await self._restore_from_backup(bot_id):
                logger.info(f"✅ Бот {bot_id} відновлено з резервної копії")
                self._reset_recovery_attempts(bot_id)
                return True
            
            logger.error(f"❌ Не вдалося відновити бота {bot_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Помилка відновлення бота {bot_id}: {e}")
            return False
    
    async def _try_reconnect(self, bot_id: str) -> bool:
        """Спроба перепідключення"""
        if not self.manager or bot_id not in self.manager.active_bots:
            return False
        
        bot_info = self.manager.active_bots[bot_id]
        client = bot_info.get('client')
        
        if not client:
            return False
        
        try:
            await client.connect()
            
            if hasattr(client, 'is_user_authorized'):
                if await client.is_user_authorized():
                    bot_info['data']['status'] = 'active'
                    bot_info['data']['last_recovery'] = datetime.now()
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Reconnect failed for {bot_id}: {e}")
            return False
    
    async def _rotate_proxy_and_retry(self, bot_id: str) -> bool:
        """Ротація проксі та повторна спроба"""
        if not self.manager or bot_id not in self.manager.active_bots:
            return False
        
        new_proxy = await self._get_next_proxy()
        
        if not new_proxy:
            logger.debug(f"No available proxy for {bot_id}")
            return False
        
        bot_info = self.manager.active_bots[bot_id]
        
        try:
            bot_info['data']['proxy_config'] = new_proxy
            bot_info['data']['proxy_last_rotated'] = datetime.now()
            
            return await self._try_reconnect(bot_id)
            
        except Exception as e:
            logger.error(f"Proxy rotation failed for {bot_id}: {e}")
            return False
    
    async def _restore_from_backup(self, bot_id: str) -> bool:
        """Відновлення з резервної копії"""
        backups = self.backup_storage.get(bot_id, [])
        
        if not backups:
            logger.debug(f"No backups available for {bot_id}")
            return False
        
        latest_backup = backups[-1]
        
        try:
            if self.manager and bot_id in self.manager.active_bots:
                bot_info = self.manager.active_bots[bot_id]
                
                for key in ['session_string', 'api_id', 'api_hash', 'device_fingerprint']:
                    if key in latest_backup:
                        bot_info['data'][key] = latest_backup[key]
                
                bot_info['data']['restored_from_backup'] = datetime.now()
                bot_info['data']['backup_version'] = latest_backup.get('version', 'unknown')
                
                return await self._try_reconnect(bot_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Restore from backup failed for {bot_id}: {e}")
            return False
    
    async def _get_next_proxy(self) -> Optional[Dict]:
        """Отримання наступного проксі з пулу"""
        if not self.proxy_pool:
            return None
        
        healthy_proxies = [
            p for p in self.proxy_pool 
            if p.get('status') != 'dead' and 
               p.get('last_failure', datetime.min) < datetime.now() - timedelta(minutes=30)
        ]
        
        if not healthy_proxies:
            return None
        
        healthy_proxies.sort(
            key=lambda p: (p.get('failure_count', 0), p.get('latency', 1000))
        )
        
        proxy = healthy_proxies[0]
        proxy['last_used'] = datetime.now()
        proxy['usage_count'] = proxy.get('usage_count', 0) + 1
        
        return proxy
    
    def add_proxy(self, proxy_config: Dict):
        """Додавання проксі до пулу"""
        proxy = {
            'host': proxy_config.get('host'),
            'port': proxy_config.get('port'),
            'username': proxy_config.get('username'),
            'password': proxy_config.get('password'),
            'type': proxy_config.get('type', 'socks5'),
            'status': 'active',
            'added_at': datetime.now(),
            'failure_count': 0,
            'usage_count': 0,
            'latency': None,
        }
        
        self.proxy_pool.append(proxy)
        logger.info(f"Proxy added: {proxy['host']}:{proxy['port']}")
    
    def remove_proxy(self, host: str, port: int):
        """Видалення проксі з пулу"""
        self.proxy_pool = [
            p for p in self.proxy_pool 
            if not (p['host'] == host and p['port'] == port)
        ]
    
    def mark_proxy_failed(self, host: str, port: int):
        """Позначення проксі як failed"""
        for proxy in self.proxy_pool:
            if proxy['host'] == host and proxy['port'] == port:
                proxy['failure_count'] = proxy.get('failure_count', 0) + 1
                proxy['last_failure'] = datetime.now()
                
                if proxy['failure_count'] >= 5:
                    proxy['status'] = 'dead'
                break
    
    async def create_backup(self, bot_id: str, bot_data: Dict) -> bool:
        """Створення резервної копії бота"""
        try:
            backup = {
                'bot_id': bot_id,
                'created_at': datetime.now().isoformat(),
                'version': hashlib.md5(
                    f"{bot_id}{datetime.now().isoformat()}".encode()
                ).hexdigest()[:8],
                'session_string': bot_data.get('session_string'),
                'api_id': bot_data.get('api_id'),
                'api_hash': bot_data.get('api_hash'),
                'device_fingerprint': bot_data.get('device_fingerprint'),
                'proxy_config': bot_data.get('proxy_config'),
                'phone': bot_data.get('phone'),
            }
            
            if bot_id not in self.backup_storage:
                self.backup_storage[bot_id] = []
            
            self.backup_storage[bot_id].append(backup)
            
            max_backups = self.settings['max_backups_per_bot']
            if len(self.backup_storage[bot_id]) > max_backups:
                self.backup_storage[bot_id] = self.backup_storage[bot_id][-max_backups:]
            
            logger.info(f"Backup created for {bot_id}: {backup['version']}")
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed for {bot_id}: {e}")
            return False
    
    def get_backups(self, bot_id: str) -> List[Dict]:
        """Отримання списку резервних копій бота"""
        return self.backup_storage.get(bot_id, [])
    
    def delete_backups(self, bot_id: str):
        """Видалення всіх резервних копій бота"""
        if bot_id in self.backup_storage:
            del self.backup_storage[bot_id]
    
    def _is_in_cooldown(self, bot_id: str) -> bool:
        """Перевірка чи бот в cooldown відновлення"""
        return False
    
    def _reset_recovery_attempts(self, bot_id: str):
        """Скидання лічильника спроб відновлення"""
        self.recovery_attempts[bot_id] = 0
    
    async def batch_recover(self, bot_ids: List[str]) -> Dict[str, bool]:
        """Масове відновлення ботів"""
        results = {}
        
        for bot_id in bot_ids:
            results[bot_id] = await self.auto_recover_bot(bot_id)
            await asyncio.sleep(1)
        
        return results
    
    async def health_check_proxies(self) -> Dict:
        """Перевірка здоров'я всіх проксі"""
        results = {
            'total': len(self.proxy_pool),
            'active': 0,
            'dead': 0,
            'avg_latency': 0,
        }
        
        latencies = []
        
        for proxy in self.proxy_pool:
            if proxy.get('status') == 'active':
                results['active'] += 1
                if proxy.get('latency'):
                    latencies.append(proxy['latency'])
            else:
                results['dead'] += 1
        
        if latencies:
            results['avg_latency'] = sum(latencies) / len(latencies)
        
        return results
    
    def get_proxy_stats(self) -> List[Dict]:
        """Отримання статистики по проксі"""
        return [
            {
                'host': p.get('host'),
                'port': p.get('port'),
                'type': p.get('type'),
                'status': p.get('status'),
                'usage_count': p.get('usage_count', 0),
                'failure_count': p.get('failure_count', 0),
                'latency': p.get('latency'),
            }
            for p in self.proxy_pool
        ]
    
    def format_recovery_report(self, bot_id: str) -> str:
        """Форматування звіту відновлення"""
        backups = self.get_backups(bot_id)
        attempts = self.recovery_attempts.get(bot_id, 0)
        
        report = (
            f"<b>🔄 RECOVERY STATUS: {bot_id}</b>\n"
            f"═══════════════════════\n\n"
            f"├ <b>Recovery attempts:</b> {attempts}/{self.max_recovery_attempts}\n"
            f"├ <b>Backups available:</b> {len(backups)}\n"
        )
        
        if backups:
            latest = backups[-1]
            report += f"├ <b>Latest backup:</b> {latest.get('created_at', 'N/A')}\n"
            report += f"└ <b>Backup version:</b> {latest.get('version', 'N/A')}\n"
        else:
            report += f"└ <b>No backups available</b>\n"
        
        return report


recovery_system = RecoverySystem()
