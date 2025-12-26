import logging
import asyncio
import socket
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import dns.resolver
    import dns.reversename
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython not available - DNS lookups disabled")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available - HTTP requests disabled")


class OSINTService:
    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.cache_ttl = 3600
    
    async def dns_lookup(self, domain: str) -> Dict[str, Any]:
        if not DNS_AVAILABLE:
            return {"status": "error", "message": "DNS module not available"}
        
        cache_key = f"dns_{domain}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        result = {
            "domain": domain,
            "status": "success",
            "records": {},
            "timestamp": datetime.now().isoformat()
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        for rtype in record_types:
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 5
                resolver.lifetime = 10
                answers = resolver.resolve(domain, rtype)
                result['records'][rtype] = [str(r) for r in answers]
            except dns.resolver.NXDOMAIN:
                result['status'] = 'nxdomain'
                result['message'] = 'Domain does not exist'
                break
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NoNameservers:
                result['records'][rtype] = []
            except Exception as e:
                logger.debug(f"DNS {rtype} lookup failed for {domain}: {e}")
        
        self.cache[cache_key] = {'data': result, 'timestamp': datetime.now()}
        return result
    
    async def reverse_dns(self, ip: str) -> Dict[str, Any]:
        if not DNS_AVAILABLE:
            return {"status": "error", "message": "DNS module not available"}
        
        try:
            addr = dns.reversename.from_address(ip)
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(addr, 'PTR')
            hostnames = [str(r) for r in answers]
            return {
                "status": "success",
                "ip": ip,
                "hostnames": hostnames
            }
        except Exception as e:
            return {"status": "error", "ip": ip, "message": str(e)}
    
    async def whois_lookup(self, domain: str) -> Dict[str, Any]:
        if not AIOHTTP_AVAILABLE:
            return {"status": "error", "message": "aiohttp not available"}
        
        cache_key = f"whois_{domain}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=at_demo&domainName={domain}&outputFormat=JSON"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            "status": "success",
                            "domain": domain,
                            "data": data.get("WhoisRecord", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                        self.cache[cache_key] = {'data': result, 'timestamp': datetime.now()}
                        return result
                    else:
                        return {"status": "error", "message": f"API returned {response.status}"}
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Request timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def ip_geolocation(self, ip: str) -> Dict[str, Any]:
        if not AIOHTTP_AVAILABLE:
            return {"status": "error", "message": "aiohttp not available"}
        
        cache_key = f"geo_{ip}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://ip-api.com/json/{ip}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            "status": "success",
                            "ip": ip,
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "region": data.get("regionName"),
                            "city": data.get("city"),
                            "zip": data.get("zip"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "as": data.get("as"),
                            "timestamp": datetime.now().isoformat()
                        }
                        self.cache[cache_key] = {'data': result, 'timestamp': datetime.now()}
                        return result
                    else:
                        return {"status": "error", "message": f"API returned {response.status}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def port_scan(self, host: str, ports: List[int] = None) -> Dict[str, Any]:
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 5432, 8080, 8443]
        
        result = {
            "status": "success",
            "host": host,
            "open_ports": [],
            "closed_ports": [],
            "timestamp": datetime.now().isoformat()
        }
        
        async def check_port(port: int) -> tuple:
            try:
                future = asyncio.open_connection(host, port)
                reader, writer = await asyncio.wait_for(future, timeout=2)
                writer.close()
                await writer.wait_closed()
                return (port, True)
            except:
                return (port, False)
        
        tasks = [check_port(p) for p in ports]
        results = await asyncio.gather(*tasks)
        
        for port, is_open in results:
            if is_open:
                result["open_ports"].append(port)
            else:
                result["closed_ports"].append(port)
        
        return result
    
    async def email_verify(self, email: str) -> Dict[str, Any]:
        if not DNS_AVAILABLE:
            return {"status": "error", "message": "DNS module not available"}
        
        try:
            domain = email.split('@')[1] if '@' in email else None
            if not domain:
                return {"status": "error", "message": "Invalid email format"}
            
            resolver = dns.resolver.Resolver()
            mx_records = []
            try:
                answers = resolver.resolve(domain, 'MX')
                mx_records = [str(r.exchange) for r in answers]
            except:
                pass
            
            return {
                "status": "success",
                "email": email,
                "domain": domain,
                "has_mx": len(mx_records) > 0,
                "mx_records": mx_records,
                "format_valid": '@' in email and '.' in domain
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_cache(self):
        self.cache.clear()

osint_service = OSINTService()
