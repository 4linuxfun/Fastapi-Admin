import io
import base64
import random
import string
import time
import hashlib
from PIL import Image, ImageDraw, ImageFont
from app.settings import settings


class CaptchaTool:
    """
    无状态验证码工具类
    生成的验证码key结构: base64(code|timestamp|signature)
    """

    @staticmethod
    def _get_signature(code: str, timestamp: int) -> str:
        """生成签名"""
        raw = f"{code.lower()}{timestamp}{settings.secret_key}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def generate(length: int = 4):
        """
        生成验证码
        :return: (base64_image, captcha_key)
        """
        # 生成纯数字验证码
        code = "".join(random.choice(string.digits) for _ in range(length))

        # 使用 Pillow 直接生成清晰、平直的图片
        width, height = 160, 60
        image = Image.new("RGB", (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)

        # 尝试加载字体，优先使用系统字体，失败则使用默认
        try:
            # 尝试加载常见字体，字号设为 40
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            try:
                # linux 常见字体
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40
                )
            except IOError:
                font = ImageFont.load_default()

        # 计算文字位置使其居中
        try:
            bbox = draw.textbbox((0, 0), code, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # 兼容旧版 Pillow
            text_width, text_height = draw.textsize(code, font=font)

        x = (width - text_width) / 2
        y = (height - text_height) / 2

        # 绘制文字（黑色）
        draw.text((x, y), code, font=font, fill=(0, 0, 0))

        # 转base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_src = f"data:image/png;base64,{base64_image}"

        # 生成Key
        timestamp = int(time.time())
        signature = CaptchaTool._get_signature(code, timestamp)

        # 组合 raw key: code|timestamp|signature
        raw_key = f"{code}|{timestamp}|{signature}"
        captcha_key = base64.b64encode(raw_key.encode("utf-8")).decode("utf-8")

        return image_src, captcha_key

    @staticmethod
    def verify(captcha_key: str, captcha_code: str, expire_seconds: int = 300) -> bool:
        """
        验证验证码
        :param captcha_key: 前端传回的 key
        :param captcha_code: 用户输入的 code
        :param expire_seconds: 过期时间
        :return: bool
        """
        if not captcha_key or not captcha_code:
            return False

        try:
            # 解码Key
            raw_key = base64.b64decode(captcha_key).decode("utf-8")
            code, timestamp_str, signature = raw_key.split("|")
            timestamp = int(timestamp_str)

            # 1. 检查过期
            if time.time() - timestamp > expire_seconds:
                return False

            # 2. 检查签名 (防篡改)
            if signature != CaptchaTool._get_signature(code, timestamp):
                return False

            # 3. 检查验证码匹配 (忽略大小写)
            return code.lower() == captcha_code.lower()

        except Exception:
            return False
