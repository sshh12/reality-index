import os
import markdown
from postmarker.core import PostmarkClient
from typing import List, Optional, Dict
from backend.database.models import Subscription
from .topic_config import get_display_name

# Email configuration
FROM_EMAIL = "noreply@reality-index.sshh.io"


class SubscriptionEmailSender:
    """Email sender for subscription-based newsletters"""
    
    def __init__(self):
        self.api_key = os.environ.get("POSTMARK_API_KEY")
        if not self.api_key:
            raise ValueError("POSTMARK_API_KEY environment variable not set")
        
        self.client = PostmarkClient(server_token=self.api_key)
        
        # Get base URL for unsubscribe links
        self.base_url = os.environ.get("BASE_URL", "https://reality-index.sshh.io")
    
    def ensure_section_titles_bolded(self, markdown_content: str) -> str:
        """Ensure section titles like 'THE MARKET MOVES:', 'MARKET MOVES:', etc. are properly bolded"""
        import re
        
        # Common section patterns that should be bolded
        section_patterns = [
            r'^(THE MARKET MOVES?:?)$',
            r'^(MARKET MOVES?:?)$', 
            r'^(THE WEEKLY THESIS:?)$',
            r'^(WEEKLY THESIS:?)$',
            r'^(THE SIGNAL SNAPSHOT:?)$',
            r'^(SIGNAL SNAPSHOT:?)$',
            r'^(KEY PREDICTIONS:?)$',
            r'^(PREDICTIONS:?)$',
            r'^(THE BOTTOM LINE:?)$',
            r'^(BOTTOM LINE:?)$',
            r'^(WHAT TO WATCH:?)$',
            r'^(WATCHING:?)$',
            r'^(THE OUTLOOK:?)$',
            r'^(OUTLOOK:?)$'
        ]
        
        lines = markdown_content.split('\n')
        processed_lines = []
        
        for line in lines:
            original_line = line
            stripped_line = line.strip()
            
            # Check if this line matches any section pattern and isn't already bolded
            if stripped_line and not stripped_line.startswith('**'):
                for pattern in section_patterns:
                    if re.match(pattern, stripped_line, re.IGNORECASE):
                        # Make it bold by wrapping in **
                        line = line.replace(stripped_line, f"**{stripped_line}**")
                        break
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def markdown_to_html(self, markdown_content: str, unsubscribe_url: str) -> str:
        """Convert markdown content to HTML with newsletter styling and unsubscribe link"""
        
        # Pre-process markdown to ensure section titles are properly bolded
        processed_content = self.ensure_section_titles_bolded(markdown_content)
        
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.nl2br'
        ])
        
        # Convert markdown to HTML
        html_body = md.convert(processed_content)
        
        # Add unsubscribe footer
        unsubscribe_footer = f"""
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
            <p style="margin: 0; color: #6b7280; font-size: 14px;">
                Don't want to receive these emails? 
                <a href="{unsubscribe_url}" style="color: #3b82f6; text-decoration: none;">Unsubscribe here</a>
            </p>
            <p style="margin: 8px 0 0 0; color: #9ca3af; font-size: 12px;">
                The Reality Index • AI-Generated Prediction Market Newsletter
            </p>
        </div>
        """
        
        # Wrap in a complete HTML document with newsletter styling
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Reality Index Newsletter</title>
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9fafb;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }}
        h1 {{
            color: #1f2937;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        h2 {{
            color: #374151;
            border-left: 4px solid #3b82f6;
            padding-left: 15px;
            margin-top: 30px;
            font-weight: 600;
        }}
        h3 {{
            color: #4b5563;
            margin-top: 25px;
            font-weight: 600;
        }}
        h4 {{
            color: #6b7280;
            margin-top: 20px;
            font-weight: 600;
        }}
        strong {{
            font-weight: 600;
            color: #1f2937;
        }}
        p {{
            margin-bottom: 15px;
        }}
        ul, ol {{
            margin-bottom: 15px;
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        blockquote {{
            border-left: 4px solid #e5e7eb;
            margin: 20px 0;
            padding-left: 20px;
            font-style: italic;
            color: #6b7280;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #e5e7eb;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f9fafb;
            font-weight: 600;
        }}
        code {{
            background-color: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f3f4f6;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        .emoji {{
            font-style: normal;
        }}
        strong {{
            color: #1f2937;
        }}
        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
            h2 {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
        {unsubscribe_footer}
    </div>
</body>
</html>
        """
        
        return html_template
    
    def extract_ai_title(self, newsletter_content: str) -> Optional[str]:
        """Extract AI-generated title from newsletter markdown content"""
        if not newsletter_content:
            return None
        
        lines = newsletter_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()  # Remove "# " prefix
        
        return None
    
    def send_newsletter_to_subscribers(self, newsletter_content: str, subscribers: List[Subscription], topics: List[str]) -> Dict:
        """Send newsletter to a list of subscribers"""
        
        if not subscribers:
            return {
                "total_recipients": 0,
                "successful_sends": 0,
                "failed_sends": 0,
                "results": []
            }
        
        # Try to extract AI-generated title, fallback to generic format
        ai_title = self.extract_ai_title(newsletter_content)
        if ai_title:
            subject = ai_title
        else:
            # Fallback to generic format
            topic_names = [get_display_name(topic) for topic in topics]
            subject = f"The Reality Index: {' + '.join(topic_names)} Weekly Update"
        
        results = []
        successful_sends = 0
        failed_sends = 0
        
        print(f"📧 Sending newsletter to {len(subscribers)} subscribers...")
        
        for subscriber in subscribers:
            try:
                # Generate unsubscribe URL
                unsubscribe_url = f"{self.base_url}/unsubscribe/{subscriber.unsubscribe_token}"
                
                # Convert markdown to HTML with unsubscribe link
                html_content = self.markdown_to_html(newsletter_content, unsubscribe_url)
                
                # Send email
                response = self.client.emails.send(
                    From=FROM_EMAIL,
                    To=subscriber.email,
                    Subject=subject,
                    HtmlBody=html_content,
                    MessageStream="outbound"
                )
                
                successful_sends += 1
                results.append({
                    "email": subscriber.email,
                    "status": "success",
                    "message_id": response.get("MessageID")
                })
                
            except Exception as e:
                failed_sends += 1
                results.append({
                    "email": subscriber.email,
                    "status": "failed",
                    "error": str(e)
                })
                print(f"   ❌ Failed to send to {subscriber.email}: {e}")
        
        return {
            "total_recipients": len(subscribers),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "results": results
        }
    
    def send_test_email(self, recipient_email: str, subject: Optional[str] = None) -> Dict:
        """Send a test email to a specific recipient"""
        
        if not subject:
            subject = "The Reality Index Newsletter - Test Email"
        
        test_content = """# Test Email

This is a test email from The Reality Index newsletter system.

## System Status
✅ Newsletter generation: Working  
✅ Email delivery: Working  
✅ Database integration: Working  

If you received this email, the system is functioning correctly!

---

**The Reality Index Team**
"""
        
        try:
            # Create a dummy unsubscribe URL for test (non-functional)
            unsubscribe_url = f"{self.base_url}/unsubscribe/test-example-token"
            html_content = self.markdown_to_html(test_content, unsubscribe_url)
            
            response = self.client.emails.send(
                From=FROM_EMAIL,
                To=recipient_email,
                Subject=subject,
                HtmlBody=html_content,
                MessageStream="outbound"
            )
            
            return {
                "total_recipients": 1,
                "successful_sends": 1,
                "failed_sends": 0,
                "results": [{
                    "email": recipient_email,
                    "status": "success",
                    "message_id": response.get("MessageID")
                }]
            }
            
        except Exception as e:
            return {
                "total_recipients": 1,
                "successful_sends": 0,
                "failed_sends": 1,
                "results": [{
                    "email": recipient_email,
                    "status": "failed",
                    "error": str(e)
                }]
            }
    
    def send_confirmation_email(self, email: str, topics: List[str], unsubscribe_token: str) -> Dict:
        """Send confirmation email to new subscriber"""
        
        topic_names = [get_display_name(topic) for topic in topics]
        subject = f"Welcome to The Reality Index - {' + '.join(topic_names)} Subscription Confirmed"
        
        confirmation_content = f"""# Welcome to The Reality Index!

## Your subscription is confirmed ✅

Thank you for subscribing to The Reality Index newsletter for **{' + '.join(topic_names)}**.

### What happens next?

📅 **When you'll receive newsletters:** Every Friday at 6:00 PM PST  
📧 **What you'll get:** AI-generated insights from prediction market data  
🎯 **Your topics:** {', '.join(topic_names)}  

### About The Reality Index

We analyze thousands of prediction markets to identify what will *actually* happen versus just opinions and media hype. Our AI processes market signals to find the most significant trends in your chosen topic areas.

**Why prediction markets?**
- 💰 Money talks louder than headlines  
- 🎯 Spot underreported stories before mainstream media  
- 🤖 AI finds signals humans miss in the noise  

### Need help?

You can unsubscribe anytime using the link in any newsletter, or visit our website to adjust your topic preferences.

---

Welcome aboard!  
**The Reality Index Team**
"""
        
        try:
            # Generate unsubscribe URL
            unsubscribe_url = f"{self.base_url}/unsubscribe/{unsubscribe_token}"
            html_content = self.markdown_to_html(confirmation_content, unsubscribe_url)
            
            response = self.client.emails.send(
                From=FROM_EMAIL,
                To=email,
                Subject=subject,
                HtmlBody=html_content,
                MessageStream="outbound"
            )
            
            return {
                "total_recipients": 1,
                "successful_sends": 1,
                "failed_sends": 0,
                "results": [{
                    "email": email,
                    "status": "success",
                    "message_id": response.get("MessageID")
                }]
            }
            
        except Exception as e:
            return {
                "total_recipients": 1,
                "successful_sends": 0,
                "failed_sends": 1,
                "results": [{
                    "email": email,
                    "status": "failed",
                    "error": str(e)
                }]
            }