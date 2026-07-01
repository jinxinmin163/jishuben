#!/usr/bin/env python3
"""Simple email proxy service - accepts POST and sends via SMTP"""
import json, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.utils import formataddr

PORT = 8899

class MailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/send":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            
            smtp_host = body.get("smtp_host", "smtp.qq.com")
            smtp_port = int(body.get("smtp_port", 587))
            smtp_user = body.get("smtp_user", "")
            smtp_pass = body.get("smtp_pass", "")
            from_addr = body.get("from_addr", smtp_user)
            from_name = body.get("from_name", "记账本")
            to_addr = body.get("to_addr", "")
            subject = body.get("subject", "记账通知")
            content = body.get("body", "")
            
            if not smtp_user or not smtp_pass or not to_addr:
                self._respond(400, {"success": False, "message": "缺少SMTP配置或收件地址"})
                return
            
            msg = MIMEMultipart()
            msg["From"] = formataddr([from_name, from_addr])
            msg["To"] = to_addr
            msg["Subject"] = subject
            msg.attach(MIMEText(content, "html", "utf-8"))
            
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            
            self._respond(200, {"success": True, "message": "发送成功"})
        except Exception as e:
            self._respond(500, {"success": False, "message": str(e)})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}", flush=True)

if __name__ == "__main__":
    print(f"Mailer starting on port {PORT}...", flush=True)
    HTTPServer(("127.0.0.1", PORT), MailHandler).serve_forever()