#!/usr/bin/env python3
"""Simple email notification service"""
import json, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.utils import formataddr

PORT = 8899
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""
FROM_NAME = "记账本通知"
TO_ADDRS = []  # list of recipient emails

class MailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in ("/send", "/api/mailer"):
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            subject = body.get("subject", "记账通知")
            content = body.get("body", "")

            if not SMTP_USER or not SMTP_PASS:
                self._respond(200, {"success": True, "message": "SMTP未配置，跳过发送"})
                return

            msg = MIMEMultipart()
            msg["From"] = formataddr([FROM_NAME, SMTP_USER])
            msg["Subject"] = subject
            msg.attach(MIMEText(content, "html", "utf-8"))

            for to_addr in TO_ADDRS:
                if to_addr.strip():
                    msg["To"] = to_addr.strip()
                    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASS)
                    server.sendmail(SMTP_USER, [to_addr.strip()], msg.as_string())
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
    HTTPServer(("0.0.0.0", PORT), MailHandler).serve_forever()
