import httpx
import json
import logging
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Resend email service client"""
    
    BASE_URL = "https://api.resend.com"
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.FROM_EMAIL
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        reply_to: str = None
    ) -> Dict[str, Any]:
        """
        Send email via Resend
        Returns: email_id, status
        """
        try:
            payload = {
                "from": self.from_email,
                "to": to,
                "subject": subject,
                "html": html_content,
            }
            
            if reply_to:
                payload["reply_to"] = reply_to
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.BASE_URL}/emails",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    logger.info(f"Email sent successfully to {to}")
                    return {
                        "success": True,
                        "email_id": data.get("id"),
                        "to": to,
                        "status": "sent"
                    }
                else:
                    logger.error(f"Email send failed: {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "to": to,
                        "status": "failed"
                    }
        
        except Exception as e:
            logger.error(f"Email service error: {e}")
            return {
                "success": False,
                "error": str(e),
                "to": to,
                "status": "error"
            }
    
    async def send_batch_emails(self, emails: list) -> Dict[str, Any]:
        """Send multiple emails"""
        results = []
        for email in emails:
            result = await self.send_email(
                to=email["to"],
                subject=email["subject"],
                html_content=email["html"]
            )
            results.append(result)
        
        return {
            "total": len(emails),
            "sent": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }

async def send_email(
    to: str,
    subject: str,
    html_content: str
) -> Dict[str, Any]:
    """Helper function to send email"""
    service = EmailService()
    return await service.send_email(to, subject, html_content)

def html_email_template(subject: str, content: str, sender_name: str = "CodeRound") -> str:
    """Convert text email to HTML"""
    return f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 5px 5px 0 0; color: white;">
                <h1 style="margin: 0; font-size: 24px;">{subject}</h1>
            </div>
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 0 0 5px 5px;">
                <div style="white-space: pre-wrap;">
{content}
                </div>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                    <p>Best regards,<br>{sender_name}</p>
                    <p>CodeRound AI - Fullstack AI Recruiter</p>
                    <p><a href="https://coderound.ai" style="color: #667eea; text-decoration: none;">www.coderound.ai</a></p>
                </div>
            </div>
        </div>
    </body>
</html>
"""
