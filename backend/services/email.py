# backend/services/email.py
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config.settings import settings
import os
import datetime

# Thiết lập logging
logger = logging.getLogger("services.email")

class EmailService:
    """
    Service xử lý gửi email
    """
    
    @staticmethod
    def send_email(to_email, subject, body, html_body=None, from_email=None):
        """
        Gửi email
        
        Args:
            to_email: Địa chỉ email người nhận
            subject: Tiêu đề email
            body: Nội dung email (text)
            html_body: Nội dung email (HTML)
            from_email: Địa chỉ email người gửi
            
        Returns:
            bool: True nếu gửi thành công, False nếu thất bại
        """
        # Kiểm tra nếu không bật tính năng email
        if not settings.MAIL_SERVER:
            logger.warning(f"[EMAIL GIẢ LẬP] Không có cấu hình SMTP. Email sẽ không được gửi thực tế.")
            logger.info(f"[EMAIL GIẢ LẬP] Đến: {to_email}")
            logger.info(f"[EMAIL GIẢ LẬP] Tiêu đề: {subject}")
            logger.info(f"[EMAIL GIẢ LẬP] Nội dung: {body[:100]}...")
            return True
            
        try:
            logger.info(f"Đang kết nối đến SMTP server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
            
            # Tạo message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            msg['To'] = to_email
            
            # Thêm phần text
            msg.attach(MIMEText(body, 'plain'))
            
            # Thêm phần HTML nếu có
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Kết nối SMTP server
            if settings.MAIL_SSL:
                logger.debug("Sử dụng SSL để kết nối SMTP")
                server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT)
            else:
                logger.debug("Khởi tạo kết nối SMTP")
                server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
                if settings.MAIL_TLS:
                    logger.debug("Sử dụng TLS để kết nối SMTP")
                    server.starttls()
            
            # Đăng nhập nếu cần
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                logger.debug(f"Đăng nhập SMTP với username: {settings.MAIL_USERNAME}")
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            else:
                logger.debug("Không sử dụng xác thực SMTP (cấu hình không có username/password)")
            
            # Gửi email
            logger.debug(f"Gửi email từ {msg['From']} đến {to_email}")
            server.sendmail(
                msg['From'],
                to_email,
                msg.as_string()
            )
            
            # Đóng kết nối
            server.quit()
            
            logger.info(f"Đã gửi email thành công đến {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi email đến {to_email}: {str(e)}")
            # Ghi log chi tiết hơn về lỗi
            if not settings.MAIL_SERVER:
                logger.error("MAIL_SERVER không được cấu hình. Vui lòng thiết lập trong file .env")
            elif not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
                logger.error("MAIL_USERNAME hoặc MAIL_PASSWORD không được cấu hình. Vui lòng thiết lập trong file .env")
            
            logger.debug(f"Chi tiết cấu hình email: Server={settings.MAIL_SERVER}, Port={settings.MAIL_PORT}, "
                        f"SSL={settings.MAIL_SSL}, TLS={settings.MAIL_TLS}")
            return False
    
    @staticmethod
    def test_smtp_connection():
        """
        Kiểm tra kết nối với SMTP server
        
        Returns:
            dict: Kết quả kiểm tra với các thông tin về trạng thái kết nối
        """
        result = {
            "success": False,
            "message": "",
            "details": {
                "server": settings.MAIL_SERVER,
                "port": settings.MAIL_PORT,
                "username": settings.MAIL_USERNAME,
                "ssl": settings.MAIL_SSL,
                "tls": settings.MAIL_TLS
            }
        }
        
        # Kiểm tra cấu hình
        if not settings.MAIL_SERVER:
            result["message"] = "MAIL_SERVER không được cấu hình"
            return result
        
        try:
            # Kết nối SMTP server
            if settings.MAIL_SSL:
                server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT)
            else:
                server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
                if settings.MAIL_TLS:
                    server.starttls()
            
            # Thêm thông tin về kết nối
            result["details"]["connection"] = "Thành công"
            
            # Đăng nhập nếu cần
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                result["details"]["authentication"] = "Thành công"
            else:
                result["details"]["authentication"] = "Không xác thực (không có username/password)"
            
            # Đóng kết nối
            server.quit()
            
            result["success"] = True
            result["message"] = "Kết nối SMTP thành công"
            
        except smtplib.SMTPAuthenticationError:
            result["message"] = "Lỗi xác thực SMTP: Username hoặc password không đúng"
            result["details"]["error"] = "Authentication failed"
            
        except smtplib.SMTPConnectError:
            result["message"] = "Không thể kết nối tới SMTP server"
            result["details"]["error"] = "Connection failed"
            
        except Exception as e:
            result["message"] = f"Lỗi khi kiểm tra kết nối SMTP: {str(e)}"
            result["details"]["error"] = str(e)
            
        return result
    
    @staticmethod
    def send_password_reset(user, reset_url):
        """
        Gửi email reset mật khẩu
        
        Args:
            user: Đối tượng User
            reset_url: URL để reset mật khẩu
            
        Returns:
            bool: True nếu gửi thành công, False nếu thất bại
        """
        subject = "Khôi phục mật khẩu"
        
        # Tạo nội dung text
        body = f"""
        Chào {user.name},
        
        Bạn đã yêu cầu khôi phục mật khẩu. Vui lòng truy cập đường dẫn sau để đặt lại mật khẩu:
        
        {reset_url}
        
        Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này.
        
        Trân trọng,
        Hệ thống phát hiện ngôn từ tiêu cực
        """
        
        # Tạo nội dung HTML
        html_body = f"""
        <html>
            <body>
                <h2>Khôi phục mật khẩu</h2>
                <p>Chào {user.name},</p>
                <p>Bạn đã yêu cầu khôi phục mật khẩu. Vui lòng truy cập đường dẫn sau để đặt lại mật khẩu:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này.</p>
                <p>Trân trọng,<br>Hệ thống phát hiện ngôn từ tiêu cực</p>
            </body>
        </html>
        """
        
        return EmailService.send_email(user.email, subject, body, html_body)
    
    @staticmethod
    def send_welcome_email(user):
        """
        Gửi email chào mừng
        
        Args:
            user: Đối tượng User
            
        Returns:
            bool: True nếu gửi thành công, False nếu thất bại
        """
        subject = "Chào mừng bạn đến với hệ thống phát hiện ngôn từ tiêu cực"
        
        # Tạo nội dung text
        body = f"""
        Chào {user.name},
        
        Chúc mừng bạn đã đăng ký thành công tài khoản. Bạn có thể bắt đầu sử dụng hệ thống ngay bây giờ.
        
        Trân trọng,
        Hệ thống phát hiện ngôn từ tiêu cực
        """
        
        # Tạo nội dung HTML
        html_body = f"""
        <html>
            <body>
                <h2>Chào mừng bạn đến với hệ thống</h2>
                <p>Chào {user.name},</p>
                <p>Chúc mừng bạn đã đăng ký thành công tài khoản. Bạn có thể bắt đầu sử dụng hệ thống ngay bây giờ.</p>
                <p>Trân trọng,<br>Hệ thống phát hiện ngôn từ tiêu cực</p>
            </body>
        </html>
        """
        
        return EmailService.send_email(user.email, subject, body, html_body)

    @staticmethod
    def send_test_email(to_email):
        """
        Gửi email test để xác nhận cấu hình SMTP hoạt động
        
        Args:
            to_email: Địa chỉ email người nhận
            
        Returns:
            dict: Kết quả gửi email test
        """
        subject = "Kiểm tra kết nối SMTP"
        body = f"""
        Đây là email kiểm tra từ hệ thống phát hiện ngôn từ tiêu cực.
        
        Thời gian: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Nếu bạn nhận được email này, cấu hình SMTP của hệ thống đã hoạt động đúng.
        
        Trân trọng,
        Hệ thống phát hiện ngôn từ tiêu cực
        """
        
        html_body = f"""
        <html>
            <body>
                <h2>Kiểm tra kết nối SMTP</h2>
                <p>Đây là email kiểm tra từ hệ thống phát hiện ngôn từ tiêu cực.</p>
                <p>Thời gian: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Nếu bạn nhận được email này, cấu hình SMTP của hệ thống đã hoạt động đúng.</p>
                <p>Trân trọng,<br>Hệ thống phát hiện ngôn từ tiêu cực</p>
            </body>
        </html>
        """
        
        result = {
            "success": False,
            "message": "",
            "to_email": to_email,
            "subject": subject,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            # Gửi email
            sent = EmailService.send_email(to_email, subject, body, html_body)
            
            if sent:
                result["success"] = True
                result["message"] = f"Email test đã được gửi thành công đến {to_email}"
            else:
                result["message"] = "Không thể gửi email test"
                
        except Exception as e:
            result["message"] = f"Lỗi khi gửi email test: {str(e)}"
            
        return result

def get_email_service():
    return EmailService

def send_reset_password_email(email, username, token):
    """
    Hàm wrapper để gửi email đặt lại mật khẩu
    
    Args:
        email: Email người dùng
        username: Tên đăng nhập
        token: Token đặt lại mật khẩu
    
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    # Tạo URL đặt lại mật khẩu với token
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # Tạo đối tượng giả user với các thuộc tính cần thiết
    class UserLike:
        def __init__(self, email, name):
            self.email = email
            self.name = name
    
    user = UserLike(email, username)
    return EmailService.send_password_reset(user, reset_url)