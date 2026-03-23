import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.html import MIMEText as MIMEHTML
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class EmailBroadcastService:
    """Service for broadcasting news via email"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
    
    async def send_newsletter(self, 
                            recipients: List[str], 
                            news_items: List[Dict[str, Any]], 
                            subject: Optional[str] = None) -> Dict[str, Any]:
        """Send newsletter with top news items"""
        try:
            if not all([self.smtp_user, self.smtp_password, self.smtp_from]):
                logger.warning("Email credentials not configured")
                return {"status": "error", "message": "Email not configured"}
            
            # Generate subject if not provided
            if not subject:
                subject = f"AI News Digest - {datetime.now().strftime('%B %d, %Y')}"
            
            # Generate HTML content
            html_content = self._generate_newsletter_html(news_items)
            text_content = self._generate_newsletter_text(news_items)
            
            # Send emails
            results = []
            for recipient in recipients:
                result = await self._send_email(
                    recipient=recipient,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content
                )
                results.append(result)
            
            success_count = sum(1 for r in results if r["status"] == "success")
            
            return {
                "status": "success",
                "recipients": len(recipients),
                "successful": success_count,
                "failed": len(recipients) - success_count,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Error sending newsletter: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_single_article(self, 
                               recipient: str, 
                               article: Dict[str, Any]) -> Dict[str, Any]:
        """Send a single article via email"""
        try:
            subject = f"AI News: {article['title']}"
            
            # Generate HTML content
            html_content = self._generate_article_html(article)
            text_content = self._generate_article_text(article)
            
            return await self._send_email(
                recipient=recipient,
                subject=subject,
                text_content=text_content,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending single article: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_email(self, 
                         recipient: str, 
                         subject: str, 
                         text_content: str, 
                         html_content: str) -> Dict[str, Any]:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from
            msg["To"] = recipient
            
            # Attach text and HTML parts
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEHTML(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            return {"status": "success", "recipient": recipient}
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            return {"status": "error", "recipient": recipient, "message": str(e)}
    
    def _generate_newsletter_html(self, news_items: List[Dict[str, Any]]) -> str:
        """Generate HTML newsletter content"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI News Digest</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px; }
                .article { border-left: 4px solid #667eea; padding: 20px; margin-bottom: 20px; background: #f9f9f9; border-radius: 5px; }
                .article h3 { margin: 0 0 10px 0; color: #333; }
                .article .source { color: #666; font-size: 0.9em; margin-bottom: 10px; }
                .article .summary { margin-bottom: 15px; }
                .article a { color: #667eea; text-decoration: none; font-weight: bold; }
                .article a:hover { text-decoration: underline; }
                .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }
                .sentiment-positive { color: #28a745; }
                .sentiment-negative { color: #dc3545; }
                .sentiment-neutral { color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI News Digest</h1>
                <p>{{ date }}</p>
            </div>
            
            {% for article in articles %}
            <div class="article">
                <h3>{{ article.title }}</h3>
                <div class="source">📰 {{ article.source }} • 📅 {{ article.published_at }}</div>
                <div class="summary">{{ article.summary }}</div>
                <div class="sentiment sentiment-{{ article.sentiment }}">
                    Sentiment: {{ article.sentiment }} • Score: {{ "%.1f"|format(article.relevance_score * 10) }}/10
                </div>
                <p><a href="{{ article.url }}">Read full article →</a></p>
            </div>
            {% endfor %}
            
            <div class="footer">
                <p>📧 This newsletter was generated by AI News Dashboard</p>
                <p>🔗 Unsubscribe | View Online</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        return template.render(
            articles=news_items[:10],  # Top 10 articles
            date=datetime.now().strftime("%B %d, %Y")
        )
    
    def _generate_newsletter_text(self, news_items: List[Dict[str, Any]]) -> str:
        """Generate plain text newsletter content"""
        content = f"AI News Digest - {datetime.now().strftime('%B %d, %Y')}\n"
        content += "=" * 50 + "\n\n"
        
        for i, article in enumerate(news_items[:10], 1):
            content += f"{i}. {article['title']}\n"
            content += f"   Source: {article['source']}\n"
            content += f"   Date: {article['published_at']}\n"
            content += f"   {article['summary']}\n"
            content += f"   Sentiment: {article['sentiment']} (Score: {article['relevance_score'] * 10:.1f}/10)\n"
            content += f"   Read more: {article['url']}\n\n"
        
        content += "-" * 50 + "\n"
        content += "Generated by AI News Dashboard\n"
        
        return content
    
    def _generate_article_html(self, article: Dict[str, Any]) -> str:
        """Generate HTML content for single article"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ article.title }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px; }
                .content { padding: 20px; background: #f9f9f9; border-radius: 5px; }
                .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
                .sentiment-positive { color: #28a745; }
                .sentiment-negative { color: #dc3545; }
                .sentiment-neutral { color: #6c757d; }
                .read-more { margin-top: 20px; }
                .read-more a { background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI News Alert</h1>
            </div>
            
            <div class="content">
                <h2>{{ article.title }}</h2>
                <div class="meta">
                    📰 {{ article.source }} • 📅 {{ article.published_at }}
                </div>
                <div class="sentiment sentiment-{{ article.sentiment }}">
                    Sentiment: {{ article.sentiment }} • Score: {{ "%.1f"|format(article.relevance_score * 10) }}/10
                </div>
                <p>{{ article.summary }}</p>
                <div class="read-more">
                    <a href="{{ article.url }}">Read full article →</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        return template.render(article=article)
    
    def _generate_article_text(self, article: Dict[str, Any]) -> str:
        """Generate plain text content for single article"""
        content = f"AI News Alert\n"
        content += "=" * 20 + "\n\n"
        content += f"{article['title']}\n\n"
        content += f"Source: {article['source']}\n"
        content += f"Date: {article['published_at']}\n"
        content += f"Sentiment: {article['sentiment']} (Score: {article['relevance_score'] * 10:.1f}/10)\n\n"
        content += f"{article['summary']}\n\n"
        content += f"Read more: {article['url']}\n"
        
        return content

# Global instance
email_broadcast_service = EmailBroadcastService()
