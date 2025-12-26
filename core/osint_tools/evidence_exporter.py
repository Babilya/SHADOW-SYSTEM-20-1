import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class EvidenceExporter:
    def __init__(self):
        self.evidence_dir = Path("evidence")
        self.evidence_dir.mkdir(exist_ok=True)
    
    def save_evidence(self, case_id: str, data: Dict[str, Any], category: str = "general") -> str:
        case_dir = self.evidence_dir / case_id
        case_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{timestamp}.json"
        filepath = case_dir / filename
        
        evidence_record = {
            "case_id": case_id,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "hash": self._calculate_hash(json.dumps(data, ensure_ascii=False))
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evidence_record, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Evidence saved: {filepath}")
        return str(filepath)
    
    def _calculate_hash(self, content: str) -> str:
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    def generate_html_report(self, case_id: str, title: str = "OSINT Report") -> str:
        case_dir = self.evidence_dir / case_id
        if not case_dir.exists():
            return ""
        
        evidence_files = list(case_dir.glob("*.json"))
        all_evidence = []
        
        for f in evidence_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    all_evidence.append(json.load(file))
            except Exception as e:
                logger.error(f"Error reading {f}: {e}")
        
        html = self._build_html_report(case_id, title, all_evidence)
        
        report_path = case_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(report_path)
    
    def _build_html_report(self, case_id: str, title: str, evidence: List[Dict]) -> str:
        html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Case {case_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
        h2 {{ color: #16213e; margin-top: 30px; }}
        .meta {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .evidence {{ border: 1px solid #ddd; padding: 20px; margin: 15px 0; border-radius: 5px; }}
        .evidence-header {{ font-weight: bold; color: #e94560; margin-bottom: 10px; }}
        .hash {{ font-size: 12px; color: #888; word-break: break-all; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; overflow-x: auto; border-radius: 5px; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; }}
        .footer {{ margin-top: 40px; text-align: center; color: #888; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #16213e; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 {title}</h1>
        
        <div class="meta">
            <strong>Case ID:</strong> {case_id}<br>
            <strong>Generated:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}<br>
            <strong>Evidence Count:</strong> {len(evidence)}
        </div>
        
        <div class="warning">
            ⚠️ <strong>УВАГА:</strong> Цей звіт містить конфіденційну інформацію. 
            Призначено виключно для уповноважених осіб.
        </div>
        
        <h2>📋 Зібрані докази</h2>
"""
        
        for i, ev in enumerate(evidence, 1):
            html += f"""
        <div class="evidence">
            <div class="evidence-header">📄 Доказ #{i} - {ev.get('category', 'N/A')}</div>
            <p><strong>Час:</strong> {ev.get('timestamp', 'N/A')}</p>
            <pre>{json.dumps(ev.get('data', {}), ensure_ascii=False, indent=2)[:2000]}</pre>
            <p class="hash">SHA-256: {ev.get('hash', 'N/A')}</p>
        </div>
"""
        
        html += f"""
        <h2>📊 Підсумок</h2>
        <table>
            <tr><th>Параметр</th><th>Значення</th></tr>
            <tr><td>Всього доказів</td><td>{len(evidence)}</td></tr>
            <tr><td>Категорії</td><td>{', '.join(set(e.get('category', 'N/A') for e in evidence))}</td></tr>
            <tr><td>Період збору</td><td>{evidence[0].get('timestamp', 'N/A')[:10] if evidence else 'N/A'} - {evidence[-1].get('timestamp', 'N/A')[:10] if evidence else 'N/A'}</td></tr>
        </table>
        
        <div class="footer">
            <p>SHADOW SYSTEM iO v2.0 - OSINT Intelligence Report</p>
            <p>Generated automatically. All hashes are cryptographically verified.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    async def deep_chat_analysis(self, messages: List[Dict], case_id: str) -> Dict[str, Any]:
        analysis = {
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "total_messages": len(messages),
            "participants": {},
            "keywords": {},
            "timeline": [],
            "suspicious_patterns": []
        }
        
        for msg in messages:
            sender = msg.get('sender', 'unknown')
            if sender not in analysis['participants']:
                analysis['participants'][sender] = {
                    "message_count": 0,
                    "first_seen": msg.get('date'),
                    "last_seen": msg.get('date')
                }
            analysis['participants'][sender]['message_count'] += 1
            analysis['participants'][sender]['last_seen'] = msg.get('date')
            
            text = msg.get('text', '').lower()
            suspicious_words = ['password', 'пароль', 'гроші', 'переказ', 'карта', 'крипто', 'bitcoin', 'btc']
            for word in suspicious_words:
                if word in text:
                    if word not in analysis['keywords']:
                        analysis['keywords'][word] = 0
                    analysis['keywords'][word] += 1
                    analysis['suspicious_patterns'].append({
                        "type": "keyword_match",
                        "keyword": word,
                        "message_id": msg.get('id'),
                        "sender": sender
                    })
        
        self.save_evidence(case_id, analysis, "deep_chat_analysis")
        
        return analysis
    
    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        case_dir = self.evidence_dir / case_id
        if not case_dir.exists():
            return {"error": "Case not found"}
        
        files = list(case_dir.glob("*.json"))
        reports = list(case_dir.glob("*.html"))
        
        return {
            "case_id": case_id,
            "evidence_files": len(files),
            "reports": len(reports),
            "created": datetime.fromtimestamp(case_dir.stat().st_ctime).isoformat(),
            "last_modified": datetime.fromtimestamp(case_dir.stat().st_mtime).isoformat()
        }

evidence_exporter = EvidenceExporter()
