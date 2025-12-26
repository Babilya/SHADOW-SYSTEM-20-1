import logging
import socket
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DNSWhoisAnalyzer:
    def get_whois_info(self, domain: str) -> Dict[str, Any]:
        try:
            import whois
            w = whois.whois(domain)
            return {
                'domain_name': w.domain_name,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date) if w.creation_date else None,
                'expiration_date': str(w.expiration_date) if w.expiration_date else None,
                'name_servers': w.name_servers,
                'registrant_country': w.country,
                'emails': w.emails,
                'org': w.org,
                'status': w.status,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {'error': 'python-whois not installed'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_dns_records(self, domain: str) -> Dict[str, Any]:
        try:
            import dns.resolver
            records = {}
            
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type] = [str(r) for r in answers]
                except dns.resolver.NoAnswer:
                    pass
                except dns.resolver.NXDOMAIN:
                    records['error'] = 'Domain does not exist'
                    break
                except Exception:
                    pass
            
            records['timestamp'] = datetime.now().isoformat()
            return records
            
        except ImportError:
            return {'error': 'dnspython not installed'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_ip_info(self, ip_address: str) -> Dict[str, Any]:
        try:
            import requests
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': ip_address,
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as'),
                    'timezone': data.get('timezone'),
                    'timestamp': datetime.now().isoformat()
                }
            return {'error': 'API request failed'}
        except Exception as e:
            return {'error': str(e)}
    
    def reverse_dns(self, ip_address: str) -> Dict[str, Any]:
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return {
                'ip': ip_address,
                'hostname': hostname,
                'timestamp': datetime.now().isoformat()
            }
        except socket.herror:
            return {'ip': ip_address, 'hostname': None, 'error': 'No PTR record'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_ssl_certificate(self, domain: str, port: int = 443) -> Dict[str, Any]:
        try:
            import ssl
            import socket
            from datetime import datetime
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'domain': domain,
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'valid_from': cert.get('notBefore'),
                        'valid_until': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber'),
                        'version': cert.get('version'),
                        'san': cert.get('subjectAltName', []),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            return {'error': str(e)}

dns_whois_analyzer = DNSWhoisAnalyzer()
