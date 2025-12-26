import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json

from core.osint_tools.telegram_analyzer import telegram_analyzer
from core.osint_tools.dns_whois import dns_whois_analyzer
from core.osint_tools.image_analyzer import image_analyzer
from core.osint_tools.social_media import social_media_osint

logger = logging.getLogger(__name__)

class OSINTAggregator:
    def __init__(self):
        self.telegram = telegram_analyzer
        self.dns = dns_whois_analyzer
        self.images = image_analyzer
        self.social = social_media_osint
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        results = {
            'target': domain,
            'type': 'domain',
            'timestamp': datetime.now().isoformat()
        }
        
        loop = asyncio.get_event_loop()
        
        whois_task = loop.run_in_executor(self.executor, self.dns.get_whois_info, domain)
        dns_task = loop.run_in_executor(self.executor, self.dns.get_dns_records, domain)
        ssl_task = loop.run_in_executor(self.executor, self.dns.check_ssl_certificate, domain)
        
        whois_result, dns_result, ssl_result = await asyncio.gather(
            whois_task, dns_task, ssl_task,
            return_exceptions=True
        )
        
        results['whois'] = whois_result if not isinstance(whois_result, Exception) else {'error': str(whois_result)}
        results['dns'] = dns_result if not isinstance(dns_result, Exception) else {'error': str(dns_result)}
        results['ssl'] = ssl_result if not isinstance(ssl_result, Exception) else {'error': str(ssl_result)}
        
        return results
    
    async def analyze_username(self, username: str) -> Dict[str, Any]:
        results = {
            'target': username,
            'type': 'username',
            'timestamp': datetime.now().isoformat()
        }
        
        loop = asyncio.get_event_loop()
        
        github_task = loop.run_in_executor(self.executor, self.social.get_github_user, username)
        availability_task = loop.run_in_executor(self.executor, self.social.check_username_availability, username)
        
        github_result, availability_result = await asyncio.gather(
            github_task, availability_task,
            return_exceptions=True
        )
        
        results['github'] = github_result if not isinstance(github_result, Exception) else {'error': str(github_result)}
        results['availability'] = availability_result if not isinstance(availability_result, Exception) else {'error': str(availability_result)}
        
        return results
    
    async def analyze_ip(self, ip_address: str) -> Dict[str, Any]:
        results = {
            'target': ip_address,
            'type': 'ip_address',
            'timestamp': datetime.now().isoformat()
        }
        
        loop = asyncio.get_event_loop()
        
        ip_info_task = loop.run_in_executor(self.executor, self.dns.get_ip_info, ip_address)
        reverse_dns_task = loop.run_in_executor(self.executor, self.dns.reverse_dns, ip_address)
        
        ip_info, reverse_dns = await asyncio.gather(
            ip_info_task, reverse_dns_task,
            return_exceptions=True
        )
        
        results['geolocation'] = ip_info if not isinstance(ip_info, Exception) else {'error': str(ip_info)}
        results['reverse_dns'] = reverse_dns if not isinstance(reverse_dns, Exception) else {'error': str(reverse_dns)}
        
        return results
    
    async def analyze_telegram_entity(self, entity: str) -> Dict[str, Any]:
        results = {
            'target': entity,
            'type': 'telegram',
            'timestamp': datetime.now().isoformat()
        }
        
        if await self.telegram.connect():
            try:
                if entity.startswith('@') or entity.startswith('https://t.me/'):
                    user_info = await self.telegram.get_user_info(entity)
                    results['user_info'] = user_info
                else:
                    channel_meta = await self.telegram.get_channel_metadata(entity)
                    results['channel_info'] = channel_meta
            finally:
                await self.telegram.disconnect()
        else:
            results['error'] = 'Telegram connection not available'
        
        return results
    
    async def full_analysis(self, target: str, analysis_type: str = 'auto') -> Dict[str, Any]:
        if analysis_type == 'auto':
            if '.' in target and not target.startswith('@'):
                if target.replace('.', '').isdigit():
                    analysis_type = 'ip'
                else:
                    analysis_type = 'domain'
            elif target.startswith('@') or target.startswith('https://t.me/'):
                analysis_type = 'telegram'
            else:
                analysis_type = 'username'
        
        if analysis_type == 'domain':
            return await self.analyze_domain(target)
        elif analysis_type == 'ip':
            return await self.analyze_ip(target)
        elif analysis_type == 'telegram':
            return await self.analyze_telegram_entity(target)
        elif analysis_type == 'username':
            return await self.analyze_username(target)
        else:
            return {'error': f'Unknown analysis type: {analysis_type}'}
    
    def generate_report(self, results: Dict[str, Any], format: str = 'text') -> str:
        if format == 'json':
            return json.dumps(results, indent=2, ensure_ascii=False, default=str)
        elif format == 'text':
            lines = [f"OSINT Report for: {results.get('target', 'Unknown')}"]
            lines.append(f"Type: {results.get('type', 'Unknown')}")
            lines.append(f"Timestamp: {results.get('timestamp', 'Unknown')}")
            lines.append("-" * 50)
            
            for key, value in results.items():
                if key not in ['target', 'type', 'timestamp']:
                    lines.append(f"\n[{key.upper()}]")
                    if isinstance(value, dict):
                        for k, v in value.items():
                            lines.append(f"  {k}: {v}")
                    else:
                        lines.append(f"  {value}")
            
            return "\n".join(lines)
        else:
            return json.dumps(results, indent=2, ensure_ascii=False, default=str)

osint_aggregator = OSINTAggregator()
