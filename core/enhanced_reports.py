"""
Enhanced Report Generator - Професійні PDF звіти
Генерація звітів з графіками та статистикою
"""
import io
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available - PDF reports disabled")


class EnhancedReportGenerator:
    """Генератор професійних звітів"""
    
    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.HEADER_COLOR = colors.HexColor('#1a237e')
            self.ACCENT_COLOR = colors.HexColor('#3f51b5')
            self.SUCCESS_COLOR = colors.HexColor('#4caf50')
            self.WARNING_COLOR = colors.HexColor('#ff9800')
            self.DANGER_COLOR = colors.HexColor('#f44336')
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        else:
            self.HEADER_COLOR = None
            self.ACCENT_COLOR = None
            self.SUCCESS_COLOR = None
            self.WARNING_COLOR = None
            self.DANGER_COLOR = None
    
    def _setup_custom_styles(self):
        """Налаштування власних стилів"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.HEADER_COLOR,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.ACCENT_COLOR,
            spaceBefore=15,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14
        ))
    
    def generate_osint_report(self, data: Dict) -> Optional[bytes]:
        """Генерація OSINT звіту"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        story.append(Paragraph("OSINT ЗВІТ", self.styles['ReportTitle']))
        story.append(Paragraph(
            f"Згенеровано: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles['ReportBody']
        ))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Загальна інформація", self.styles['SectionHeader']))
        
        info_data = [
            ["Ціль:", data.get('target', 'Не вказано')],
            ["Тип аналізу:", data.get('analysis_type', 'Повний')],
            ["Рівень ризику:", data.get('risk_level', 'Невизначено')],
            ["Статус:", data.get('status', 'Завершено')]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (0, -1), self.HEADER_COLOR),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))
        
        if data.get('findings'):
            story.append(Paragraph("Знахідки", self.styles['SectionHeader']))
            
            findings_items = []
            for finding in data['findings'][:10]:
                findings_items.append(ListItem(
                    Paragraph(str(finding), self.styles['ReportBody'])
                ))
            
            if findings_items:
                story.append(ListFlowable(findings_items, bulletType='bullet'))
            story.append(Spacer(1, 15))
        
        if data.get('threats'):
            story.append(Paragraph("Виявлені загрози", self.styles['SectionHeader']))
            
            threat_data = [["Тип", "Опис", "Рівень"]]
            for threat in data['threats'][:10]:
                threat_data.append([
                    threat.get('type', 'N/A'),
                    threat.get('description', 'N/A')[:50],
                    threat.get('level', 'N/A')
                ])
            
            threat_table = Table(threat_data, colWidths=[3*cm, 8*cm, 3*cm])
            threat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.ACCENT_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(threat_table)
            story.append(Spacer(1, 15))
        
        if data.get('recommendations'):
            story.append(Paragraph("Рекомендації", self.styles['SectionHeader']))
            
            for rec in data['recommendations'][:5]:
                story.append(Paragraph(f"• {rec}", self.styles['ReportBody']))
            story.append(Spacer(1, 15))
        
        if data.get('ai_analysis'):
            story.append(Paragraph("AI Аналіз", self.styles['SectionHeader']))
            story.append(Paragraph(
                data['ai_analysis'][:1000],
                self.styles['ReportBody']
            ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_campaign_report(self, data: Dict) -> Optional[bytes]:
        """Генерація звіту кампанії"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        story.append(Paragraph("ЗВІТ КАМПАНІЇ", self.styles['ReportTitle']))
        story.append(Paragraph(
            f"ID: {data.get('campaign_id', 'N/A')}",
            self.styles['ReportBody']
        ))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Статистика", self.styles['SectionHeader']))
        
        stats = data.get('stats', {})
        stats_data = [
            ["Метрика", "Значення"],
            ["Відправлено", str(stats.get('sent', 0))],
            ["Доставлено", str(stats.get('delivered', 0))],
            ["Прочитано", str(stats.get('read', 0))],
            ["Відповіді", str(stats.get('replied', 0))],
            ["Рейт доставки", f"{stats.get('delivery_rate', 0)}%"],
            ["Рейт відкриття", f"{stats.get('open_rate', 0)}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[6*cm, 6*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.ACCENT_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(stats_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_user_report(self, data: Dict) -> Optional[bytes]:
        """Генерація звіту по користувачу"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        story.append(Paragraph("ПРОФІЛЬ КОРИСТУВАЧА", self.styles['ReportTitle']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Основна інформація", self.styles['SectionHeader']))
        
        user_data = [
            ["ID:", str(data.get('user_id', 'N/A'))],
            ["Username:", data.get('username', 'N/A')],
            ["Тип:", data.get('user_type', 'N/A')],
            ["Роль:", data.get('role', 'N/A')],
            ["Активностей:", str(data.get('total_activities', 0))]
        ]
        
        user_table = Table(user_data, colWidths=[4*cm, 10*cm])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(user_table)
        
        if data.get('patterns'):
            story.append(Spacer(1, 15))
            story.append(Paragraph("Поведінкові патерни", self.styles['SectionHeader']))
            
            patterns = data['patterns']
            for key, value in patterns.items():
                if isinstance(value, dict):
                    value = ', '.join(f"{k}: {v}" for k, v in value.items())
                story.append(Paragraph(
                    f"<b>{key}:</b> {value}",
                    self.styles['ReportBody']
                ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


enhanced_report_generator = EnhancedReportGenerator()
