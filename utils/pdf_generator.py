import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
import base64
from datetime import datetime
import tempfile
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        custom_styles = {
            'Title': ParagraphStyle(
                'Title',
                parent=self.styles['Title'],
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors.purple,
                spaceAfter=12
            ),
            'Heading1': ParagraphStyle(
                'Heading1',
                parent=self.styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.darkblue,
                spaceAfter=8
            ),
            'Heading2': ParagraphStyle(
                'Heading2',
                parent=self.styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=12,
                textColor=colors.darkblue,
                spaceBefore=6,
                spaceAfter=6
            ),
            'Normal': ParagraphStyle(
                'Normal',
                parent=self.styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                spaceAfter=6
            ),
            'JournalEntry': ParagraphStyle(
                'JournalEntry',
                parent=self.styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=10,
                leftIndent=20,
                rightIndent=20,
                spaceAfter=12,
                borderWidth=1,
                borderColor=colors.lightgrey,
                borderPadding=8,
                borderRadius=5
            ),
            'Quote': ParagraphStyle(
                'Quote',
                parent=self.styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=10,
                leftIndent=30,
                rightIndent=30,
                spaceBefore=6,
                spaceAfter=6
            ),
            'Insight': ParagraphStyle(
                'Insight',
                parent=self.styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.darkblue,
                leftIndent=10,
                spaceAfter=6
            )
        }
        return custom_styles
    
    def create_weekly_summary_pdf(self, user_data, start_date, end_date):
        """
        Generate a PDF summary of the user's journal entries for the selected period.
        """
        # Create a BytesIO buffer
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Container for elements
        elements = []
        
        # Title
        title = Paragraph(
            f"Weekly Summary: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
            self.custom_styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Introduction
        intro = Paragraph(
            "This report summarizes your journaling activity, emotional insights, and growth highlights for the selected period.",
            self.custom_styles['Normal']
        )
        elements.append(intro)
        elements.append(Spacer(1, 12))
        
        # Filter journal entries for the selected period
        entries = [
            entry for entry in user_data.get('journal_entries', [])
            if start_date <= datetime.strptime(entry['date'], '%Y-%m-%d') <= end_date
        ]
        
        # Section 1: Activity Summary
        elements.append(Paragraph("Activity Summary", self.custom_styles['Heading1']))
        elements.append(Spacer(1, 6))
        
        # Create a summary table
        total_entries = len(entries)
        total_words = sum(len(entry['content'].split()) for entry in entries)
        
        activity_data = [
            ["Metric", "Value"],
            ["Journal Entries", str(total_entries)],
            ["Total Words Written", str(total_words)],
            ["Average Words per Entry", str(round(total_words / max(total_entries, 1)))]
        ]
        
        activity_table = Table(activity_data, colWidths=[200, 200])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lavender),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 1, colors.lightgrey)
        ]))
        
        elements.append(activity_table)
        elements.append(Spacer(1, 12))
        
        # Section 2: Emotional Insights
        if entries:
            elements.append(Paragraph("Emotional Insights", self.custom_styles['Heading1']))
            elements.append(Spacer(1, 6))
            
            # Collect emotion data
            emotions = {
                "joy": 0,
                "sadness": 0,
                "anger": 0,
                "fear": 0,
                "hope": 0
            }
            
            for entry in entries:
                if 'sentiment' in entry and 'emotions' in entry['sentiment']:
                    for emotion, value in entry['sentiment']['emotions'].items():
                        emotions[emotion] += value
            
            # Average the emotions
            for emotion in emotions:
                emotions[emotion] = round(emotions[emotion] / len(entries), 2)
            
            # Create a paragraph describing emotional trends
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            elements.append(Paragraph(
                f"Your dominant emotion during this period was <b>{dominant_emotion}</b>.",
                self.custom_styles['Normal']
            ))
            
            elements.append(Spacer(1, 12))
        
        # Section 3: Journal Entries with Insights
        elements.append(Paragraph("Journal Entries & Insights", self.custom_styles['Heading1']))
        elements.append(Spacer(1, 6))
        
        for entry in entries:
            # Entry date and module/lesson info
            date_str = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%B %d, %Y')
            module_info = f"Module {entry.get('module', '?')}, Lesson {entry.get('lesson', '?')}"
            
            elements.append(Paragraph(
                f"<b>{date_str} - {module_info}</b>",
                self.custom_styles['Heading2']
            ))
            
            # Journal content
            elements.append(Paragraph(
                entry.get('content', ''),
                self.custom_styles['JournalEntry']
            ))
            
            # Sentiment summary
            if 'sentiment' in entry:
                sentiment = entry['sentiment']
                elements.append(Paragraph(
                    f"<b>Emotional tone:</b> {sentiment.get('category', 'neutral')}",
                    self.custom_styles['Insight']
                ))
                
                # Add themes if available
                if 'themes' in entry:
                    themes = entry['themes']
                    if themes:
                        theme_text = ", ".join(themes)
                        elements.append(Paragraph(
                            f"<b>Key themes:</b> {theme_text}",
                            self.custom_styles['Insight']
                        ))
            
            elements.append(Spacer(1, 12))
        
        # Section 4: Growth Highlights and Recommendations
        elements.append(Paragraph("Growth Highlights & Recommendations", self.custom_styles['Heading1']))
        elements.append(Spacer(1, 6))
        
        # Simple growth recommendations based on emotional trends
        if entries:
            if dominant_emotion == "joy":
                elements.append(Paragraph(
                    "Your entries show a strong presence of joy. Consider exploring what activities and circumstances create this positive emotion and how you might incorporate more of them into your daily life.",
                    self.custom_styles['Normal']
                ))
            elif dominant_emotion == "hope":
                elements.append(Paragraph(
                    "Hope is prominent in your entries. This is a powerful emotion for transformation. Consider setting specific intentions that align with your hopeful outlook.",
                    self.custom_styles['Normal']
                ))
            elif dominant_emotion == "sadness":
                elements.append(Paragraph(
                    "Your entries reflect sadness during this period. This emotion often points to what matters deeply to us. Consider what losses or unmet needs might be beneath this feeling.",
                    self.custom_styles['Normal']
                ))
            elif dominant_emotion == "anger":
                elements.append(Paragraph(
                    "Anger appears as a significant emotion in your entries. Anger often signals boundary violations or unmet needs. Reflect on what boundaries you might need to establish or reinforce.",
                    self.custom_styles['Normal']
                ))
            elif dominant_emotion == "fear":
                elements.append(Paragraph(
                    "Fear emerges as a key emotion in your journal entries. Fear often highlights areas where we need more support or information. Consider what resources might help you move through this fear.",
                    self.custom_styles['Normal']
                ))
            
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(
                "For your coaching session, consider discussing:",
                self.custom_styles['Normal']
            ))
            
            recommendations = [
                f"How your experience with {dominant_emotion} relates to your growth journey",
                "Any patterns you notice in your entries that you'd like to explore further",
                "Specific goals or intentions for the coming week"
            ]
            
            for recommendation in recommendations:
                elements.append(Paragraph(
                    f"• {recommendation}",
                    self.custom_styles['Normal']
                ))
        else:
            elements.append(Paragraph(
                "No journal entries found for this period. Regular journaling will provide insights into your growth journey.",
                self.custom_styles['Normal']
            ))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value from the buffer
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def create_download_link(self, pdf_bytes, filename="summary.pdf"):
        """
        Create a download link for the generated PDF.
        """
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF</a>'
        return href
