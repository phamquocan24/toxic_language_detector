# backend/services/email.py
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config.settings import settings

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
        if not settings.SMTP_ENABLED:
            logger.info(f"Email được giả lập gửi đến {to_email}: {subject}")
            return True
            
        try:
            # Tạo message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or settings.SMTP_FROM_EMAIL
            msg['To'] = to_email
            
            # Thêm phần text
            msg.attach(MIMEText(body, 'plain'))
            
            # Thêm phần HTML nếu có
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Kết nối SMTP server
            if settings.SMTP_USE_SSL:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                if settings.SMTP_USE_TLS:
                    server.starttls()
            
            # Đăng nhập nếu cần
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            # Gửi email
            server.sendmail(
                msg['From'],
                to_email,
                msg.as_string()
            )
            
            # Đóng kết nối
            server.quit()
            
            logger.info(f"Đã gửi email đến {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi email: {str(e)}")
            return False
    
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

# Hàm để truy cập service từ bên ngoài
def get_email_service():
    """
    Trả về đối tượng EmailService
    
    Returns:
        EmailService: Đối tượng EmailService
    """
    return EmailService