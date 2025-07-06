import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys
import platform
import ctypes  # 用于设置Windows任务栏图标

# 动态导入win32gui和win32con，解决打包后导入失败问题
try:
    import win32gui
    import win32con

    WIN32GUI_AVAILABLE = True
except ImportError:
    WIN32GUI_AVAILABLE = False


    # 创建模拟类，实现必要的方法签名以避免代码错误
    class MockWin32:
        def FindWindow(self, *args, **kwargs):
            print("警告: win32gui.FindWindow不可用")
            return 0

        def GetForegroundWindow(self, *args, **kwargs):
            print("警告: win32gui.GetForegroundWindow不可用")
            return 0

        def GetTopWindow(self, *args, **kwargs):
            print("警告: win32gui.GetTopWindow不可用")
            return 0

        def GetWindowLong(self, *args, **kwargs):
            print("警告: win32gui.GetWindowLong不可用")
            return 0

        def SetWindowLong(self, *args, **kwargs):
            print("警告: win32gui.SetWindowLong不可用")
            return 0

        def LoadImage(self, *args, **kwargs):
            print("警告: win32gui.LoadImage不可用")
            return 0

        def SendMessage(self, *args, **kwargs):
            print("警告: win32gui.SendMessage不可用")
            return 0

        def ShowWindow(self, *args, **kwargs):
            print("警告: win32gui.ShowWindow不可用")
            return 0

        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                print(f"警告: 未实现的win32函数{name}被调用")
                return 0

            return mock_func


    # 实例化模拟对象
    win32gui = MockWin32()
    win32con = MockWin32()

    # 手动定义必要的win32常量
    win32con.GWL_EXSTYLE = -20
    win32con.WS_EX_APPWINDOW = 0x00040000
    win32con.WS_EX_TOOLWINDOW = 0x00000080
    win32con.IMAGE_ICON = 1
    win32con.LR_LOADFROMFILE = 0x00000010
    win32con.LR_DEFAULTSIZE = 0x00000040
    win32con.WM_SETICON = 0x0080
    win32con.ICON_BIG = 1
    win32con.ICON_SMALL = 0
    win32con.SW_HIDE = 0
    win32con.SW_SHOW = 5
    win32con.SW_SHOWNA = 8  # 新增常量

# -------------------------- 配置区域 --------------------------
# 平行四边形区域（文字）
LEFT_PARALLELOGRAM = (380, 60, 780, 90)  # (x_min, y_min, x_max, y_max)
RIGHT_PARALLELOGRAM = (1140, 60, 1540, 90)  # (x_min, y_min, x_max, y_max)

# 分数显示区域
LEFT_SCORE_REGION = (820, 60, 860, 90)  # (x_min, y_min, x_max, y_max)
RIGHT_SCORE_REGION = (1060, 60, 1100, 90)  # (x_min, y_min, x_max, y_max)

# 赛制显示区域（相对于图片的中心位置，可调整偏移量）
BOUT_REGION_OFFSET_X = 0  # X轴偏移量
BOUT_REGION_OFFSET_Y = 30  # Y轴偏移量

# 颜色配置
LEFT_COLOR = "red"  # 左侧文字和分数颜色
RIGHT_COLOR = "blue"  # 右侧文字和分数颜色
WHITEISH_COLOR = "#EEEEEE"  # 亮白灰色（比赛制文字更淡更亮）
BUTTON_BG = "#EEEEEE"  # 按钮背景色（亮白灰色）
BUTTON_FG = "black"  # 按钮文字颜色
BOUT_TEXT_COLOR = "#AAAAAA"  # 赛制文字颜色（淡灰色）
BOUT_OUTLINE_COLOR = "black"  # 赛制文字描边颜色
BOUT_DEFAULT_FONT_SIZE = 60  # 赛制默认字体大小

# 按钮位置配置（相对于窗口左上角的坐标）
LEFT_BUTTON_X = 820  # 左侧按钮X坐标
LEFT_BUTTON_Y = 110  # 左侧按钮Y坐标
RIGHT_BUTTON_X = 1025  # 右侧按钮X坐标
RIGHT_BUTTON_Y = 110  # 右侧按钮Y坐标

# 抗锯齿参数
SMOOTH_FACTOR = 2  # 用于文字渲染的缩放因子

# 版权信息
COPYRIGHT_TEXT = "By bilibili 纳瑞亚之星"

# 系统检测
CURRENT_OS = platform.system()

# 新增：赛制文字加粗配置
BOUT_FONT_WEIGHT = "bold"  # 可设置为 "bold" 或 "normal"

# 新增：图标配置
ICON_FILE = "app.ico"  # 图标文件名

# 新增：自定义图片配置
CUSTOM_IMAGE_FOLDER = "UI"  # 存放自定义图片的文件夹
DEFAULT_IMAGE_NAME = "default.png"  # 默认图片名称

# 新增：是否使用win32gui的标志
USE_WIN32GUI = WIN32GUI_AVAILABLE and CURRENT_OS == "Windows"

# 新增：自定义图片路径变量
custom_image_path = None

# 新增：配置区域范围变量
left_parallelogram = LEFT_PARALLELOGRAM
right_parallelogram = RIGHT_PARALLELOGRAM
left_score_region = LEFT_SCORE_REGION
right_score_region = RIGHT_SCORE_REGION
bout_region_offset_x = BOUT_REGION_OFFSET_X
bout_region_offset_y = BOUT_REGION_OFFSET_Y


# -------------------------------------------------------------

class ScoreboardConfigWindow:
    VERSION = "v1.0.2"  # 更新版本号

    def __init__(self, root):
        self.root = root
        self.root.title("计分板配置")
        self.root.geometry("500x650")  # 增加窗口高度以容纳区域配置
        self.root.resizable(False, False)
        self.center_window()

        # 基本配置
        self.left_score = 0
        self.right_score = 0
        self.left_text = ""
        self.right_text = ""
        self.font_size = 50  # 默认字体大小
        self.bout_number = 0  # 赛制数字
        self.image_path = None  # 图片路径

        # 区域配置
        self.left_parallelogram = LEFT_PARALLELOGRAM
        self.right_parallelogram = RIGHT_PARALLELOGRAM
        self.left_score_region = LEFT_SCORE_REGION
        self.right_score_region = RIGHT_SCORE_REGION
        self.bout_region_offset_x = BOUT_REGION_OFFSET_X
        self.bout_region_offset_y = BOUT_REGION_OFFSET_Y

        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="计分板配置", font=("黑体", 16, "bold"))
        title_label.pack(pady=(10, 5))

        # 基本信息配置区域
        basic_frame = tk.LabelFrame(self.root, text="基本信息", font=("黑体", 12))
        basic_frame.pack(fill=tk.X, padx=30, pady=5, ipady=5)

        # 左侧文字
        left_frame = tk.Frame(basic_frame)
        left_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_frame, text="左侧文字:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.left_entry = tk.Entry(left_frame, font=("黑体", 12))
        self.left_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 右侧文字
        right_frame = tk.Frame(basic_frame)
        right_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_frame, text="右侧文字:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.right_entry = tk.Entry(right_frame, font=("黑体", 12))
        self.right_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 左侧分数
        left_score_frame = tk.Frame(basic_frame)
        left_score_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_score_frame, text="左侧初始分:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.left_score_entry = tk.Entry(left_score_frame, font=("黑体", 12), width=5)
        self.left_score_entry.insert(0, str(self.left_score))
        self.left_score_entry.pack(side=tk.LEFT)

        # 右侧分数
        right_score_frame = tk.Frame(basic_frame)
        right_score_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_score_frame, text="右侧初始分:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.right_score_entry = tk.Entry(right_score_frame, font=("黑体", 12), width=5)
        self.right_score_entry.insert(0, str(self.right_score))
        self.right_score_entry.pack(side=tk.LEFT)

        # 字体大小
        font_frame = tk.Frame(basic_frame)
        font_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(font_frame, text="字体大小:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.font_entry = tk.Entry(font_frame, font=("黑体", 12), width=5)
        self.font_entry.insert(0, str(self.font_size))
        self.font_entry.pack(side=tk.LEFT)

        # 赛制输入
        bout_frame = tk.Frame(basic_frame)
        bout_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(bout_frame, text="赛制(BO):", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.bout_entry = tk.Entry(bout_frame, font=("黑体", 12), width=5)
        self.bout_entry.pack(side=tk.LEFT)

        # 图片选择区域
        image_frame = tk.Frame(basic_frame)
        image_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(image_frame, text="背景图片:", width=10, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        # 图片路径显示
        self.image_path_var = tk.StringVar()
        self.image_path_var.set("未选择图片")
        image_path_label = tk.Label(image_frame, textvariable=self.image_path_var, font=("黑体", 10),
                                    fg="gray", wraplength=200, justify=tk.LEFT)
        image_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # 浏览按钮
        browse_button = tk.Button(image_frame, text="浏览", command=self.browse_image,
                                  font=("黑体", 10), bg=BUTTON_BG)
        browse_button.pack(side=tk.RIGHT)

        # 区域配置部分
        region_frame = tk.LabelFrame(self.root, text="区域配置", font=("黑体", 12))
        region_frame.pack(fill=tk.X, padx=30, pady=5, ipady=5)

        # 左侧名称区域
        left_name_frame = tk.Frame(region_frame)
        left_name_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_name_frame, text="左侧名称区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        self.left_name_entries = []
        for i, value in enumerate(self.left_parallelogram):
            entry = tk.Entry(left_name_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            self.left_name_entries.append(entry)

        tk.Label(left_name_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 右侧名称区域
        right_name_frame = tk.Frame(region_frame)
        right_name_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_name_frame, text="右侧名称区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        self.right_name_entries = []
        for i, value in enumerate(self.right_parallelogram):
            entry = tk.Entry(right_name_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            self.right_name_entries.append(entry)

        tk.Label(right_name_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 左侧分数区域
        left_score_region_frame = tk.Frame(region_frame)
        left_score_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_score_region_frame, text="左侧分数区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                  padx=(0, 5))

        self.left_score_region_entries = []
        for i, value in enumerate(self.left_score_region):
            entry = tk.Entry(left_score_region_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            self.left_score_region_entries.append(entry)

        tk.Label(left_score_region_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 右侧分数区域
        right_score_region_frame = tk.Frame(region_frame)
        right_score_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_score_region_frame, text="右侧分数区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                   padx=(0, 5))

        self.right_score_region_entries = []
        for i, value in enumerate(self.right_score_region):
            entry = tk.Entry(right_score_region_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            self.right_score_region_entries.append(entry)

        tk.Label(right_score_region_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT,
                                                                                                    padx=5)

        # 赛制区域
        bout_region_frame = tk.Frame(region_frame)
        bout_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(bout_region_frame, text="赛制区域偏移:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        self.bout_offset_x_entry = tk.Entry(bout_region_frame, font=("黑体", 10), width=6)
        self.bout_offset_x_entry.insert(0, str(self.bout_region_offset_x))
        self.bout_offset_x_entry.pack(side=tk.LEFT, padx=2)

        self.bout_offset_y_entry = tk.Entry(bout_region_frame, font=("黑体", 10), width=6)
        self.bout_offset_y_entry.insert(0, str(self.bout_region_offset_y))
        self.bout_offset_y_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(bout_region_frame, text="(X偏移,Y偏移)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="确认", command=self.confirm, width=10, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                     padx=10)
        tk.Button(button_frame, text="取消", command=self.root.destroy, width=10, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                          padx=10)

        # 底部信息（左下角版本号，右下角版权）
        bottom_frame = tk.Frame(self.root, bg='white')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        bottom_frame = tk.Frame(self.root, bg='white')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # 左侧版本号
        version_label = tk.Label(
            bottom_frame,
            text=f"版本: {self.VERSION}",
            font=("黑体", 10),
            fg="gray",
            bg='white'
        )
        version_label.pack(side=tk.LEFT, padx=10)

        # 右侧版权信息
        copyright_label = tk.Label(
            bottom_frame,
            text=COPYRIGHT_TEXT,
            font=("黑体", 10),
            fg="gray",
            bg='white'
        )
        copyright_label.pack(side=tk.RIGHT, padx=10)

    def browse_image(self):
        """浏览并选择图片"""
        file_path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if file_path:
            self.image_path = file_path
            self.image_path_var.set(os.path.basename(file_path))

    def confirm(self):
        # 获取基本信息
        self.left_text = self.left_entry.get()
        self.right_text = self.right_entry.get()

        # 验证分数输入
        try:
            self.left_score = int(self.left_score_entry.get())
            self.right_score = int(self.right_score_entry.get())
        except ValueError:
            messagebox.showerror("错误", "分数必须为整数")
            return

        # 验证字体大小
        try:
            self.font_size = int(self.font_entry.get())
            if not (10 <= self.font_size <= 200):
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "字体大小必须在10-200之间")
            return

        # 验证赛制输入
        bout_text = self.bout_entry.get().strip()
        if bout_text:
            try:
                self.bout_number = int(bout_text)
                if self.bout_number <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "赛制必须为正整数")
                return
        else:
            self.bout_number = 0  # 不显示赛制

        # 获取区域配置
        try:
            # 左侧名称区域
            self.left_parallelogram = tuple(int(entry.get()) for entry in self.left_name_entries)
            # 右侧名称区域
            self.right_parallelogram = tuple(int(entry.get()) for entry in self.right_name_entries)
            # 左侧分数区域
            self.left_score_region = tuple(int(entry.get()) for entry in self.left_score_region_entries)
            # 右侧分数区域
            self.right_score_region = tuple(int(entry.get()) for entry in self.right_score_region_entries)
            # 赛制区域偏移
            self.bout_region_offset_x = int(self.bout_offset_x_entry.get())
            self.bout_region_offset_y = int(self.bout_offset_y_entry.get())
        except ValueError:
            messagebox.showerror("错误", "区域配置必须为整数")
            return

        self.root.destroy()


class TransparentScoreboardApp:
    def __init__(self, root, left_text, right_text, left_score, right_score, font_size, bout_number,
                 left_parallelogram, right_parallelogram,
                 left_score_region, right_score_region,
                 bout_region_offset_x, bout_region_offset_y,
                 image_path=None):
        self.root = root
        # 设置窗口标题
        self.root.title("心灵终结计分板")

        # 设置应用程序ID（确保任务栏分组正确）
        if CURRENT_OS == "Windows":
            try:
                # 设置应用程序ID，这有助于在任务栏中正确显示图标
                myappid = 'com.mindcontrol.scoreboard.1.0'  # 任意字符串，建议使用反向域名格式
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except:
                print("警告: 无法设置应用程序ID")

        # 修改：使用Windows API确保无标题栏时任务栏显示图标
        if CURRENT_OS == "Windows" and USE_WIN32GUI:
            self.root.overrideredirect(True)  # 完全自定义窗口（无标题栏）
            self.root.attributes('-topmost', True)
            self.root.wm_attributes('-transparentcolor', 'white')
            # 延迟获取窗口句柄并设置样式（确保窗口已创建）
            self.root.after(100, self.fix_windows_taskbar_icon)  # 延迟100ms执行
        else:
            # Linux和macOS保留简化窗口装饰
            self.root.overrideredirect(False)
            self.root.attributes('-topmost', True)
            if CURRENT_OS != "Windows":
                self.root.attributes('-type', 'splash')  # Linux/macOS隐藏标题栏

        self.image_path = image_path or self.find_image_path()  # 使用传入的图片路径或查找默认图片
        self.icon_path = self.find_icon_path()  # 查找图标路径

        # 设置图标
        self.set_window_icon()

        # 核心配置参数
        self.left_text = left_text
        self.right_text = right_text
        self.left_score = left_score
        self.right_score = right_score
        self.font_size = font_size
        self.bout_number = bout_number  # 赛制数字
        self.font_path = self.find_font_path()

        # 区域配置
        self.left_region = left_parallelogram
        self.right_region = right_parallelogram
        self.left_score_region = left_score_region
        self.right_score_region = right_score_region
        self.bout_region_offset_x = bout_region_offset_x
        self.bout_region_offset_y = bout_region_offset_y

        # 区域与颜色配置
        self.left_color = LEFT_COLOR  # 左侧文字和分数颜色
        self.right_color = RIGHT_COLOR  # 右侧文字和分数颜色
        self.outline_color = WHITEISH_COLOR  # 描边颜色改为亮白灰色

        # 初始化界面
        self.load_and_display_image()
        self.position_window()
        self.create_control_panel()
        self.create_floating_buttons()  # 创建浮动按钮

        # 拖动相关参数
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        # 绑定事件
        self.root.bind("<Button-1>", self.on_drag_start)
        self.root.bind("<B1-Motion>", self.on_drag_motion)
        self.root.bind("<Escape>", self.quit_app)
        self.root.bind("<Button-3>", self.toggle_minimize)  # 右键点击最小化

    def find_icon_path(self):
        """查找图标文件路径"""
        # 尝试当前目录
        if os.path.exists(ICON_FILE):
            return ICON_FILE

        # 尝试当前目录下的resources文件夹
        resources_dir = os.path.join(os.getcwd(), "resources")
        if os.path.exists(resources_dir) and os.path.isdir(resources_dir):
            icon_path = os.path.join(resources_dir, ICON_FILE)
            if os.path.exists(icon_path):
                return icon_path

        # 尝试使用PyInstaller打包后的临时目录
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, ICON_FILE)
            if os.path.exists(icon_path):
                return icon_path

        return None

    def set_window_icon(self):
        """设置窗口图标"""
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                if CURRENT_OS == "Windows":
                    # Windows系统使用ico文件
                    self.root.iconbitmap(self.icon_path)
                else:
                    # Linux/macOS系统使用图片文件（尝试转换为支持的格式）
                    try:
                        # 尝试将ICO转换为Tkinter可用的格式
                        icon = Image.open(self.icon_path)
                        icon = icon.resize((32, 32), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(icon)
                        self.root.tk.call('wm', 'iconphoto', self.root._w, photo)
                    except:
                        # 如果转换失败，尝试直接使用图片
                        self.root.tk.call('wm', 'iconphoto', self.root._w, ImageTk.PhotoImage(file=self.icon_path))
                print("成功设置窗口图标")
            except Exception as e:
                print(f"警告: 无法设置窗口图标: {e}")
        else:
            print(f"警告: 找不到图标文件: {ICON_FILE}")

    def fix_windows_taskbar_icon(self):
        """修复Windows系统下无标题栏窗口的任务栏图标显示问题"""
        if not USE_WIN32GUI:
            print("警告: win32gui不可用，无法修复任务栏图标显示")
            return

        try:
            # 获取当前窗口句柄（多种方式确保获取成功）
            hwnd = None
            # 尝试通过标题查找
            hwnd = win32gui.FindWindow(None, "心灵终结计分板")
            if not hwnd:
                # 尝试获取前台窗口
                hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                # 尝试获取顶级窗口
                hwnd = win32gui.GetTopWindow(None)

            if hwnd:
                # 获取当前窗口样式
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                # 添加WS_EX_APPWINDOW样式，确保任务栏显示
                ex_style |= win32con.WS_EX_APPWINDOW
                # 移除WS_EX_TOOLWINDOW样式，避免窗口被归类为工具窗口
                ex_style &= ~win32con.WS_EX_TOOLWINDOW
                # 应用新样式
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

                # 如果有图标，设置窗口图标
                if self.icon_path and os.path.exists(self.icon_path):
                    icon_handle = win32gui.LoadImage(
                        None,
                        self.icon_path,
                        win32con.IMAGE_ICON,
                        0, 0,
                        win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                    )
                    if icon_handle:
                        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, icon_handle)
                        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon_handle)

                # 刷新窗口显示（先隐藏再显示）
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                print("任务栏图标显示修复成功")
        except Exception as e:
            print(f"修复任务栏图标时出错: {e}")

    def toggle_minimize(self, event):
        """右键点击最小化窗口"""
        if self.root.state() == "normal":
            self.root.iconify()
        else:
            self.root.deiconify()

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径（适配PyInstaller打包）"""
        if getattr(sys, 'frozen', False):
            # 打包后环境：获取临时目录路径
            base_path = sys._MEIPASS
        else:
            # 开发环境：使用当前文件所在目录
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def find_image_path(self):
        """查找图片路径，支持不同系统的路径格式"""
        global custom_image_path

        # 如果有自定义图片路径，优先使用
        if custom_image_path and os.path.exists(custom_image_path):
            return custom_image_path

        # 尝试UI文件夹
        ui_dir = self.get_resource_path(CUSTOM_IMAGE_FOLDER)
        if os.path.exists(ui_dir) and os.path.isdir(ui_dir):
            # 查找默认图片
            default_path = os.path.join(ui_dir, DEFAULT_IMAGE_NAME)
            if os.path.exists(default_path):
                return default_path

            # 查找UI文件夹中的任何图片
            for file in os.listdir(ui_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    return os.path.join(ui_dir, file)

        # 如果找不到，尝试当前目录
        for file in os.listdir(os.getcwd()):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                return os.path.join(os.getcwd(), file)

        # 如果仍然找不到，返回None
        return None

    def find_font_path(self):
        """查找黑体字体路径，针对不同系统优化"""
        if CURRENT_OS == "Windows":
            win_fonts = [
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            ]
            for font_path in win_fonts:
                if os.path.exists(font_path):
                    return font_path

        elif CURRENT_OS == "Linux":
            linux_fonts = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Noto Sans CJK
                "/usr/share/fonts/truetype/simhei.ttf",  # 常见黑体路径
            ]
            for font_path in linux_fonts:
                if os.path.exists(font_path):
                    return font_path

        elif CURRENT_OS == "Darwin":  # macOS
            mac_fonts = [
                "/System/Library/Fonts/PingFang.ttc",  # 苹方
                "/Library/Fonts/SimHei.ttf",  # 黑体
                "/System/Library/Fonts/STHeiti Medium.ttc",  # 华文黑体
            ]
            for font_path in mac_fonts:
                if os.path.exists(font_path):
                    return font_path

        # 如果找不到指定字体，返回None
        return None

    def load_and_display_image(self):
        try:
            if not self.image_path or not os.path.exists(self.image_path):
                # 创建一个默认的空白图像
                width, height = 1920, 1080
                self.original_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(self.original_image)
                font = ImageFont.load_default()
                draw.text((width // 2, height // 2), "未找到背景图片", font=font, fill=(255, 0, 0))
            else:
                self.original_image = Image.open(self.image_path).convert("RGBA")

            self.display_image = self.original_image.copy()
            self.update_image_display()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            # 创建一个错误图像
            width, height = 800, 600
            self.original_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(self.original_image)
            font = ImageFont.load_default()
            draw.text((width // 2, height // 2), f"错误: {str(e)}", font=font, fill=(255, 0, 0))
            self.display_image = self.original_image.copy()
            self.update_image_display()

    def update_image_display(self):
        self.display_image = self.original_image.copy()
        draw = ImageDraw.Draw(self.display_image)

        # 如果找不到指定字体，使用系统默认字体
        if self.font_path and os.path.exists(self.font_path):
            try:
                base_font = ImageFont.truetype(self.font_path, self.font_size)
            except:
                print("警告: 无法加载指定字体，使用默认字体")
                base_font = ImageFont.load_default()
        else:
            print("警告: 未找到黑体字体，使用默认字体")
            base_font = ImageFont.load_default()

        def get_fitted_font(text, region):
            x_min, y_min, x_max, y_max = region
            region_width = x_max - x_min
            for size in range(self.font_size, 10, -1):
                try:
                    if self.font_path and os.path.exists(self.font_path):
                        font = ImageFont.truetype(self.font_path, size)
                    else:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width <= region_width * 0.9:
                    return font
            return base_font

        # 绘制左侧文字（红色）
        if self.left_text and self.left_region:
            x_min, y_min, x_max, y_max = self.left_region
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            font = get_fitted_font(self.left_text, self.left_region)
            bbox = draw.textbbox((0, 0), self.left_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            self.draw_text_with_outline(draw, text_x, text_y, self.left_text, font, self.outline_color, self.left_color)

        # 绘制右侧文字（蓝色）
        if self.right_text and self.right_region:
            x_min, y_min, x_max, y_max = self.right_region
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            font = get_fitted_font(self.right_text, self.right_region)
            bbox = draw.textbbox((0, 0), self.right_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            self.draw_text_with_outline(draw, text_x, text_y, self.right_text, font=font,
                                        outline_color=self.outline_color,
                                        fill_color=self.right_color)

        # 绘制左侧分数（与左侧文字同色：红色）
        if self.left_score_region:
            x_min, y_min, x_max, y_max = self.left_score_region
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            score_text = str(self.left_score)
            font = get_fitted_font(score_text, self.left_score_region)
            bbox = draw.textbbox((0, 0), score_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            self.draw_text_with_outline(draw, text_x, text_y, score_text, font, self.outline_color, self.left_color)

        # 绘制右侧分数（与右侧文字同色：蓝色）
        if self.right_score_region:
            x_min, y_min, x_max, y_max = self.right_score_region
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            score_text = str(self.right_score)
            font = get_fitted_font(score_text, self.right_score_region)
            bbox = draw.textbbox((0, 0), score_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            self.draw_text_with_outline(draw, text_x, text_y, score_text, font, self.outline_color, self.right_color)

        # 绘制赛制显示（如果有设置）
        if self.bout_number > 0:
            bout_text = f"BO{self.bout_number}"
            img_width, img_height = self.display_image.size
            center_x = img_width // 2 + self.bout_region_offset_x
            center_y = img_height // 2 + self.bout_region_offset_y

            # 确定字体大小（使用新的默认值60）
            bout_font_size = min(BOUT_DEFAULT_FONT_SIZE, 200)  # 限制最大大小
            try:
                if self.font_path and os.path.exists(self.font_path):
                    # 尝试加载粗体字体
                    if CURRENT_OS == "Windows":
                        # Windows系统使用字体文件直接加载
                        bout_font = ImageFont.truetype(self.font_path, bout_font_size)
                    else:
                        # 其他系统尝试通过字体名指定粗体
                        bout_font = ImageFont.truetype(self.font_path, bout_font_size)
                else:
                    # 使用系统默认字体
                    try:
                        # 尝试创建粗体字体
                        bout_font = ImageFont.truetype("Arial", bout_font_size, encoding="unic")
                    except:
                        # 失败则使用默认字体
                        bout_font = ImageFont.load_default()
            except:
                # 出错则使用默认字体
                bout_font = ImageFont.load_default()

            # 计算文本包围盒
            bbox = draw.textbbox((0, 0), bout_text, font=bout_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 计算文本位置
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2

            # 使用现有的描边函数绘制赛制文本（淡灰色字体黑色描边）
            self.draw_text_with_outline(draw, text_x, text_y, bout_text, bout_font, BOUT_OUTLINE_COLOR, BOUT_TEXT_COLOR)

        self.photo = ImageTk.PhotoImage(self.display_image)
        if hasattr(self, 'image_label'):
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo
        else:
            self.image_label = tk.Label(self.root, image=self.photo, bg='white')
            self.image_label.pack()

    def draw_text_with_outline(self, draw, x, y, text, font, outline_color, fill_color):
        """改进的文字描边绘制方法，确保描边不透明"""
        # 绘制文字描边（增加描边宽度以增强效果）
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        # 绘制主文字（使用指定颜色）
        draw.text((x, y), text, font=font, fill=fill_color)

    def create_control_panel(self):
        # 底部控制面板
        control_frame = tk.Frame(self.root, bg='white')
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 左侧文字控制
        left_frame = tk.Frame(control_frame, bg='white')
        left_frame.pack(side=tk.LEFT, padx=10, pady=2)
        tk.Label(left_frame, text="左侧文字:", bg='white', font=("黑体", 12)).pack(side=tk.LEFT)
        left_entry = tk.Entry(left_frame, width=15, font=("黑体", 12))
        left_entry.insert(0, self.left_text)
        left_entry.pack(side=tk.LEFT, padx=5)

        # 右侧文字控制
        right_frame = tk.Frame(control_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, padx=10, pady=2)
        tk.Label(right_frame, text="右侧文字:", bg='white', font=("黑体", 12)).pack(side=tk.LEFT)
        right_entry = tk.Entry(right_frame, width=15, font=("黑体", 12))
        right_entry.insert(0, self.right_text)
        right_entry.pack(side=tk.LEFT, padx=5)

        # 功能按钮区
        button_frame = tk.Frame(control_frame, bg='white')
        button_frame.pack(side=tk.TOP, pady=2)

        # 更新文字按钮
        update_button = tk.Button(button_frame, text="更新文字",
                                  command=lambda: self.update_text(
                                      left_entry.get(),
                                      right_entry.get()
                                  ),
                                  font=("黑体", 12), bg=BUTTON_BG)
        update_button.pack(side=tk.LEFT, padx=5)

        # 调整字体大小按钮
        font_button = tk.Button(button_frame, text="调整字体大小",
                                command=self.change_font_size,
                                font=("黑体", 12), bg=BUTTON_BG)
        font_button.pack(side=tk.LEFT, padx=5)

        # 调整赛制按钮
        bout_button = tk.Button(button_frame, text="调整赛制",
                                command=self.change_bout_number,
                                font=("黑体", 12), bg=BUTTON_BG)
        bout_button.pack(side=tk.LEFT, padx=5)

        # 新增：更换图片按钮
        change_image_button = tk.Button(button_frame, text="更换图片",
                                        command=self.change_image,
                                        font=("黑体", 12), bg=BUTTON_BG)
        change_image_button.pack(side=tk.LEFT, padx=5)

        # 新增：调整区域按钮
        region_button = tk.Button(button_frame, text="调整区域",
                                  command=self.change_regions,
                                  font=("黑体", 12), bg=BUTTON_BG)
        region_button.pack(side=tk.LEFT, padx=5)

        # 关闭按钮
        close_button = tk.Button(button_frame, text="关闭",
                                 command=self.quit_app,
                                 font=("黑体", 12), bg=BUTTON_BG)
        close_button.pack(side=tk.LEFT, padx=5)

        # 新增：最小化按钮
        minimize_button = tk.Button(button_frame, text="最小化",
                                    command=self.root.iconify,
                                    font=("黑体", 12), bg=BUTTON_BG)
        minimize_button.pack(side=tk.LEFT, padx=5)

    def change_image(self):
        """更换背景图片"""
        global custom_image_path

        file_path = filedialog.askopenfilename(
            title="选择新的背景图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if file_path:
            # 保存自定义图片路径
            custom_image_path = file_path
            self.image_path = file_path
            self.load_and_display_image()
            messagebox.showinfo("成功", "背景图片已更新")

    def change_regions(self):
        """调整区域范围对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("调整区域范围")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建区域输入框
        region_frame = tk.LabelFrame(dialog, text="区域配置", font=("黑体", 12))
        region_frame.pack(fill=tk.X, padx=30, pady=5, ipady=5)

        # 左侧名称区域
        left_name_frame = tk.Frame(region_frame)
        left_name_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_name_frame, text="左侧名称区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        left_name_entries = []
        for i, value in enumerate(self.left_region):
            entry = tk.Entry(left_name_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            left_name_entries.append(entry)

        tk.Label(left_name_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 右侧名称区域
        right_name_frame = tk.Frame(region_frame)
        right_name_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_name_frame, text="右侧名称区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        right_name_entries = []
        for i, value in enumerate(self.right_region):
            entry = tk.Entry(right_name_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            right_name_entries.append(entry)

        tk.Label(right_name_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 左侧分数区域
        left_score_region_frame = tk.Frame(region_frame)
        left_score_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(left_score_region_frame, text="左侧分数区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                  padx=(0, 5))

        left_score_region_entries = []
        for i, value in enumerate(self.left_score_region):
            entry = tk.Entry(left_score_region_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            left_score_region_entries.append(entry)

        tk.Label(left_score_region_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 右侧分数区域
        right_score_region_frame = tk.Frame(region_frame)
        right_score_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(right_score_region_frame, text="右侧分数区域:", width=12, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                   padx=(0, 5))

        right_score_region_entries = []
        for i, value in enumerate(self.right_score_region):
            entry = tk.Entry(right_score_region_frame, font=("黑体", 10), width=6)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=2)
            right_score_region_entries.append(entry)

        tk.Label(right_score_region_frame, text="(x1,y1,x2,y2)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT,
                                                                                                    padx=5)

        # 赛制区域
        bout_region_frame = tk.Frame(region_frame)
        bout_region_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(bout_region_frame, text="赛制区域偏移:", width=12, font=("黑体", 12)).pack(side=tk.LEFT, padx=(0, 5))

        bout_offset_x_entry = tk.Entry(bout_region_frame, font=("黑体", 10), width=6)
        bout_offset_x_entry.insert(0, str(self.bout_region_offset_x))
        bout_offset_x_entry.pack(side=tk.LEFT, padx=2)

        bout_offset_y_entry = tk.Entry(bout_region_frame, font=("黑体", 10), width=6)
        bout_offset_y_entry.insert(0, str(self.bout_region_offset_y))
        bout_offset_y_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(bout_region_frame, text="(X偏移,Y偏移)", font=("黑体", 10), fg="gray").pack(side=tk.LEFT, padx=5)

        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def confirm_changes():
            try:
                # 更新区域配置
                self.left_region = tuple(int(entry.get()) for entry in left_name_entries)
                self.right_region = tuple(int(entry.get()) for entry in right_name_entries)
                self.left_score_region = tuple(int(entry.get()) for entry in left_score_region_entries)
                self.right_score_region = tuple(int(entry.get()) for entry in right_score_region_entries)
                self.bout_region_offset_x = int(bout_offset_x_entry.get())
                self.bout_region_offset_y = int(bout_offset_y_entry.get())

                # 更新显示
                self.update_image_display()

                # 关闭对话框
                dialog.destroy()

                messagebox.showinfo("成功", "区域配置已更新")
            except ValueError:
                messagebox.showerror("错误", "区域配置必须为整数")

        tk.Button(button_frame, text="确认", command=confirm_changes, width=10, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                        padx=10)
        tk.Button(button_frame, text="取消", command=dialog.destroy, width=10, font=("黑体", 12)).pack(side=tk.LEFT,
                                                                                                       padx=10)

    def create_floating_buttons(self):
        """创建浮动的分数控制按钮"""
        # 左侧分数控制按钮
        left_button_frame = tk.Frame(self.root, bg=BUTTON_BG, bd=1, relief=tk.RAISED)
        left_button_frame.place(x=LEFT_BUTTON_X, y=LEFT_BUTTON_Y)

        # 左侧减分按钮
        tk.Button(left_button_frame, text="-",
                  command=lambda: self.update_score("left", -1),
                  bg=self.left_color, fg="white",
                  font=("黑体", 14, "bold"),
                  width=2, height=1).pack(side=tk.LEFT, padx=2)

        # 左侧加分按钮
        tk.Button(left_button_frame, text="+",
                  command=lambda: self.update_score("left", 1),
                  bg=self.left_color, fg="white",
                  font=("黑体", 14, "bold"),
                  width=2, height=1).pack(side=tk.LEFT, padx=2)

        # 右侧分数控制按钮
        right_button_frame = tk.Frame(self.root, bg=BUTTON_BG, bd=1, relief=tk.RAISED)
        right_button_frame.place(x=RIGHT_BUTTON_X, y=RIGHT_BUTTON_Y)

        # 右侧减分按钮
        tk.Button(right_button_frame, text="-",
                  command=lambda: self.update_score("right", -1),
                  bg=self.right_color, fg="white",
                  font=("黑体", 14, "bold"),
                  width=2, height=1).pack(side=tk.LEFT, padx=2)

        # 右侧加分按钮
        tk.Button(right_button_frame, text="+",
                  command=lambda: self.update_score("right", 1),
                  bg=self.right_color, fg="white",
                  font=("黑体", 14, "bold"),
                  width=2, height=1).pack(side=tk.LEFT, padx=2)

    def update_text(self, left_text, right_text):
        """更新左右侧文字并重新渲染"""
        self.left_text = left_text
        self.right_text = right_text
        self.update_image_display()

    def update_score(self, side, delta):
        """更新分数并重新渲染"""
        if side == "left":
            self.left_score += delta
            # 确保分数不小于0
            self.left_score = max(0, self.left_score)
            if hasattr(self, 'left_score_label'):
                self.left_score_label.config(text=str(self.left_score))
        else:
            self.right_score += delta
            # 确保分数不小于0
            self.right_score = max(0, self.right_score)
            if hasattr(self, 'right_score_label'):
                self.right_score_label.config(text=str(self.right_score))
        self.update_image_display()

    def change_font_size(self):
        """调整字体大小对话框"""
        current_size = self.font_size
        new_size = simpledialog.askinteger(
            "字体大小",
            "请输入新的字体大小(10-200):",
            minvalue=10,
            maxvalue=200,
            initialvalue=current_size
        )
        if new_size:
            self.font_size = new_size
            self.update_image_display()

    def change_bout_number(self):
        """调整赛制数字对话框"""
        current_bout = self.bout_number
        new_bout = simpledialog.askinteger(
            "赛制设置",
            "请输入赛制数字(1-99):",
            minvalue=1,
            maxvalue=99,
            initialvalue=current_bout if current_bout > 0 else 5
        )
        if new_bout:
            self.bout_number = new_bout
            self.update_image_display()

    def position_window(self):
        """定位窗口至屏幕顶部居中"""
        if not hasattr(self, 'photo'):
            return
        img_width, img_height = self.photo.width(), self.photo.height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算初始位置（顶部居中）
        x = (screen_width - img_width) // 2
        y = 0  # 调整为顶部对齐

        # 确保窗口不超出屏幕边界
        x = max(0, min(x, screen_width - img_width))
        y = max(0, min(y, screen_height - img_height))

        self.root.geometry(f"{img_width}x{img_height}+{x}+{y}")

    def on_drag_start(self, event):
        """开始拖动窗口"""
        if event.widget == self.image_label:
            self.dragging = True
            self.offset_x = event.x
            self.offset_y = event.y

    def on_drag_motion(self, event):
        """拖动窗口过程"""
        if self.dragging:
            new_x = self.root.winfo_pointerx() - self.offset_x
            new_y = self.root.winfo_pointery() - self.offset_y
            self.root.geometry(f"+{new_x}+{new_y}")

    def quit_app(self, event=None):
        """关闭应用"""
        self.root.destroy()


def main():
    # 启动配置窗口
    config_root = tk.Tk()
    config_window = ScoreboardConfigWindow(config_root)

    # 设置配置窗口图标
    icon_path = find_icon_path()
    if icon_path and os.path.exists(icon_path):
        try:
            config_root.iconbitmap(icon_path)
        except:
            print("警告: 无法设置配置窗口图标")

    config_root.mainloop()

    # 获取配置参数
    left_text = config_window.left_text
    right_text = config_window.right_text
    left_score = config_window.left_score
    right_score = config_window.right_score
    font_size = config_window.font_size
    bout_number = config_window.bout_number
    image_path = config_window.image_path  # 获取用户选择的图片路径

    # 获取区域配置
    left_parallelogram = config_window.left_parallelogram
    right_parallelogram = config_window.right_parallelogram
    left_score_region = config_window.left_score_region
    right_score_region = config_window.right_score_region
    bout_region_offset_x = config_window.bout_region_offset_x
    bout_region_offset_y = config_window.bout_region_offset_y

    # 启动主窗口
    if left_text or right_text or left_score is not None or right_score is not None:
        root = tk.Tk()
        root.title("心灵终结计分板")  # 设置窗口标题，显示在任务栏
        app = TransparentScoreboardApp(
            root, left_text, right_text,
            left_score, right_score, font_size, bout_number,
            left_parallelogram, right_parallelogram,
            left_score_region, right_score_region,
            bout_region_offset_x, bout_region_offset_y,
            image_path
        )
        root.mainloop()


def find_icon_path():
    """查找图标文件路径（独立函数，用于main函数）"""
    # 尝试当前目录
    if os.path.exists(ICON_FILE):
        return ICON_FILE

    # 尝试当前目录下的resources文件夹
    resources_dir = os.path.join(os.getcwd(), "resources")
    if os.path.exists(resources_dir) and os.path.isdir(resources_dir):
        icon_path = os.path.join(resources_dir, ICON_FILE)
        if os.path.exists(icon_path):
            return icon_path

    # 尝试使用PyInstaller打包后的临时目录
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        icon_path = os.path.join(base_path, ICON_FILE)
        if os.path.exists(icon_path):
            return icon_path

    return None


if __name__ == "__main__":
    main()