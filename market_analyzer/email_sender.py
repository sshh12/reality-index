import os
import markdown
from postmarker.core import PostmarkClient
from typing import List, Optional

# Email configuration
FROM_EMAIL = "noreply@state.sshh.io"


class NewsletterEmailSender:
    def __init__(self):
        self.api_key = os.environ.get("POSTMARK_API_KEY")
        if not self.api_key:
            raise ValueError("POSTMARK_API_KEY environment variable not set")
        
        self.client = PostmarkClient(server_token=self.api_key)
        
        # Get email list from environment
        emails_str = os.environ.get("TO_EMAILS", "")
        if not emails_str:
            raise ValueError("TO_EMAILS environment variable not set")
        
        self.to_emails = [email.strip() for email in emails_str.split(",") if email.strip()]
        if not self.to_emails:
            raise ValueError("No valid emails found in TO_EMAILS")
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to HTML with proper newsletter styling"""
        
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.nl2br'
        ])
        
        # Convert markdown to HTML
        html_body = md.convert(markdown_content)
        
        # Wrap in a complete HTML document with newsletter styling
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket Newsletter</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .newsletter-container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #34495e;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        strong {{
            color: #2980b9;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
        }}
        code {{
            background-color: #f1f2f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f1f2f6;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }}
        .market-data {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        {html_body}
        <div class="footer">
            <p>This newsletter was generated from Polymarket data analysis.</p>
        </div>
    </div>
</body>
</html>
"""
        return html_template
    
    def extract_subject_from_content(self, markdown_content: str) -> str:
        """Extract subject line from the first H1 heading"""
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                # Remove the # and clean up
                subject = line[2:].strip()
                # Remove any markdown formatting
                subject = subject.replace('**', '').replace('*', '')
                return subject
        
        # Fallback subject
        return "Polymarket Newsletter Update"
    
    def send_newsletter(self, markdown_content: str, subject: Optional[str] = None) -> dict:
        """Send newsletter to all configured email addresses"""
        
        if not subject:
            subject = self.extract_subject_from_content(markdown_content)
        
        html_content = self.markdown_to_html(markdown_content)
        
        results = []
        
        for email in self.to_emails:
            try:
                response = self.client.emails.send(
                    From=FROM_EMAIL,
                    To=email,
                    Subject=subject,
                    HtmlBody=html_content,
                    MessageStream="outbound"
                )
                
                results.append({
                    "email": email,
                    "status": "sent",
                    "message_id": response["MessageID"]
                })
                
            except Exception as e:
                results.append({
                    "email": email,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "total_recipients": len(self.to_emails),
            "successful_sends": len([r for r in results if r["status"] == "sent"]),
            "failed_sends": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
    
    def send_test_email(self, subject: Optional[str] = None) -> dict:
        """Send a test email to all configured recipients"""
        
        if not subject:
            subject = "Polymarket Newsletter Test Email"
        
        test_content = """# Test Email from Polymarket Newsletter System

This is a test email to verify that your email configuration is working properly.

## System Information
- Email system: ✅ Working
- Postmark API: ✅ Connected  
- HTML formatting: ✅ Applied

## What this means
If you're receiving this email, your Polymarket newsletter email system is configured correctly and ready to send actual market analysis newsletters.

---

**This is an automated test email. No market data was analyzed for this message.**
"""
        
        html_content = self.markdown_to_html(test_content)
        
        results = []
        
        for email in self.to_emails:
            try:
                response = self.client.emails.send(
                    From=FROM_EMAIL,
                    To=email,
                    Subject=subject,
                    HtmlBody=html_content,
                    MessageStream="outbound"
                )
                
                results.append({
                    "email": email,
                    "status": "sent",
                    "message_id": response["MessageID"]
                })
                
            except Exception as e:
                results.append({
                    "email": email,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "total_recipients": len(self.to_emails),
            "successful_sends": len([r for r in results if r["status"] == "sent"]),
            "failed_sends": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
    
    def get_config_summary(self) -> dict:
        """Get current email configuration"""
        return {
            "postmark_configured": bool(self.api_key),
            "recipient_count": len(self.to_emails),
            "recipients": self.to_emails
        }