import base64
import random
from PIL import Image  # pip install Pillow
from PIL import ImageDraw  # 画笔对象
from PIL import ImageFont  # 字体对象
from io import BytesIO  # 可将数据写到内存中


class AuthCode(object):

    def __init__(self, digits=5, is_letter=False, image_size=(245, 40), font_path='kumo.ttf', font_size=36,
                 is_interfering_line=True,
                 interfering_line_count=1,
                 is_interfering_point=True,
                 interfering_point_count=10,
                 is_save_disk=False,
                 save_disk_path=None,  # 保存到磁盘的路径，如果保存至磁盘，则必须save_disk_path
                 is_save_memory=True):
        """
        内部功能全部通过传参调用
        :param digits: 验证码长度
        :param is_letter: 验证码是否包含字母
        :param image_size: 图片大小 ("宽度", "高度")
        :param font_path: 字体文件路径
        :param font_size: 生成的字体大小
        :param is_interfering_line: 是否给图片加干扰线
        :param interfering_line_count: 干扰线数量
        :param is_interfering_point: 是否给图片加干扰点
        :param interfering_point_count: 干扰点数量
        :param is_save_disk: 默认保存到磁盘
        :param save_disk_path: 保存到磁盘的路径，如果保存至磁盘，则必须传入一个有效路径
        :param is_save_memory: 是否保存到内存(以便传输)
        """
        self.digits = digits
        self.is_letter = is_letter
        self.image_size = image_size
        self.font_path = font_path
        self.font_size = font_size
        self.is_interfering_line = is_interfering_line
        self.interfering_line_count = interfering_line_count
        self.is_interfering_point = is_interfering_point
        self.interfering_point_count = interfering_point_count
        self.is_save_disk = is_save_disk
        self.save_disk_path = save_disk_path
        self.is_save_memory = is_save_memory

        self.__code = self.__code_s() if self.is_letter else self.__code()  # 获取验证码
        img_obj, draw_obj = self.__image()
        # 开始在图片上写验证码
        [draw_obj.text((i * 56, 0), self.__code[i], self.__rgb_color(), self.__font()) for i in range(self.digits)]
        # 是否增加干扰属性
        self.is_interfering_line and self.__add_interfering_line(draw_obj)
        self.is_interfering_point and self.__add_interfering_point(draw_obj)
        # 将完工的图片保存
        self.is_save_disk and self.__save_to_disk(img_obj)
        self.is_save_memory and self.__save_to_memory(img_obj)

    def get_code(self):
        """用于获取生成的验证码内容"""
        return self.__code

    def get_memory_img_data(self):
        """用于获取保存在内存中的图片"""
        return base64.b64encode(self.__img_data)

    def __save_to_disk(self, img_obj):
        """将图片保存到磁盘"""
        with open(self.save_disk_path, 'wb') as f:
            img_obj.save(f, format='png')

    def __save_to_memory(self, img_obj):
        """保存至内存"""
        f = BytesIO()
        img_obj.save(f, format='png')
        self.__img_data = f.getvalue()

    def __code(self):
        """数字验证码"""
        return [str(random.randint(0, 9)) for i in range(self.digits)]

    def __code_s(self):
        """数字字母验证码"""
        code = ''
        for i in range(self.digits):
            big_letter = chr(random.randint(65, 90))  # 大写字母
            small_letter = chr(random.randint(97, 122))  # 小写字母
            num = str(random.randint(0, 9))
            code += random.choice([big_letter, small_letter, num])
        return code

    def __rgb_color(self):
        """随机返回RBG颜色类型的三个值"""
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def __image(self):
        """返回一个图片对象和这个图片对象的画笔对象"""
        img_obj = Image.new('RGB', self.image_size, self.__rgb_color())  # 生成一个图片对象
        # img_obj = Image.new("颜色类型", (图片宽度, 图片高度), (RGB的三个值))
        draw_obj = ImageDraw.Draw(img_obj)  # 在该图片对象上生成一个画笔对象
        return img_obj, draw_obj

    def __font(self):
        """返回一个字体对象, 需先下载字体"""
        # return ImageFont.truetype("字体路径", "字体大小")
        return ImageFont.truetype(self.font_path, self.font_size)

    def __add_interfering_line(self, draw_obj):
        """加干扰线"""
        width, height = self.image_size  # 图片高宽(防止越界)
        for i in range(self.interfering_line_count):
            x1 = random.randint(0, width)
            x2 = random.randint(0, width)
            y1 = random.randint(0, height)
            y2 = random.randint(0, height)
            draw_obj.line((x1, y1, x2, y2), fill=self.__rgb_color())

    def __add_interfering_point(self, draw_obj):
        """加干扰点"""
        width, height = self.image_size  # 图片高宽(防止越界)
        for i in range(self.interfering_point_count):
            draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=self.__rgb_color())
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw_obj.arc((x, y, x + 4, y + 4), 0, 90, fill=self.__rgb_color())


if __name__ == '__main__':
    # 生成验证码
    obj = AuthCode(font_path='字体文件路径')

    # 获取验证码内容
    obj.get_code()

    # 获取保存在内存中的验证码数据
    obj.get_memory_img_data()
