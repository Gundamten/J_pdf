import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader

def natural_sort_key(s):
    """
    用于自然排序的键函数
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def convert_images_to_pdf(image_folder, output_pdf, page_size=letter, progress_callback=None):
    """
    将指定文件夹中的所有图片转换为一个PDF文件。
    :param image_folder: 包含图片的文件夹路径。
    :param output_pdf: 输出的PDF文件路径。
    :param page_size: PDF页面大小，可以是 'letter' 或 'A4'。
    :param progress_callback: 进度回调函数，用于更新GUI。
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 获取页面尺寸
        if page_size.lower() == 'a4':
            pagesize = A4
        else:
            pagesize = letter

        # 创建PDF画布
        c = canvas.Canvas(output_pdf, pagesize=pagesize)
        width, height = pagesize

        # 支持的图片文件扩展名
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')

        # 获取图片列表并进行自然排序
        image_files = sorted(
            [f for f in os.listdir(image_folder) if f.lower().endswith(image_extensions)],
            key=natural_sort_key
        )
        total = len(image_files)

        if total == 0:
            if progress_callback:
                progress_callback("错误：未找到图片文件")
            return

        for i, filename in enumerate(image_files):
            image_path = os.path.join(image_folder, filename)
            if progress_callback:
                progress_callback(f"正在处理 ({i + 1}/{total})：{filename}")

            try:
                img_reader = ImageReader(image_path)
                img_width, img_height = img_reader.getSize()

                # 计算缩放比例
                margin = 20
                max_img_width = width - 2 * margin
                max_img_height = height - 2 * margin
                scale = min(max_img_width / img_width, max_img_height / img_height)
                if scale > 1:
                    scale = 1

                new_width = img_width * scale
                new_height = img_height * scale

                # 居中绘制
                x = (width - new_width) / 2
                y = (height - new_height) / 2
                c.drawImage(img_reader, x, y, width=new_width, height=new_height)
                c.showPage()

            except Exception as e:
                if progress_callback:
                    progress_callback(f"警告：处理 {filename} 失败 - {str(e)}")

        c.save()
        if progress_callback:
            progress_callback(f"成功！PDF已保存至：{output_pdf}")

    except Exception as e:
        if progress_callback:
            progress_callback(f"转换失败：{str(e)}")

class ImageToPdfApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转PDF工具")
        self.root.geometry("600x300")  # 窗口大小

        # 变量
        self.image_folder = tk.StringVar()
        self.output_pdf = tk.StringVar()
        self.page_size = tk.StringVar(value="A4")  # 默认A4

        # UI布局
        self.create_widgets()

    def create_widgets(self):
        # 框架1：选择图片文件夹
        frame1 = tk.Frame(self.root, pady=10)
        frame1.pack(fill=tk.X, padx=20)

        tk.Label(frame1, text="图片文件夹：", width=12).pack(side=tk.LEFT)
        tk.Entry(frame1, textvariable=self.image_folder, state='readonly', width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="浏览...", command=self.select_image_folder).pack(side=tk.LEFT)

        # 框架2：选择输出PDF
        frame2 = tk.Frame(self.root, pady=10)
        frame2.pack(fill=tk.X, padx=20)

        tk.Label(frame2, text="输出PDF：", width=12).pack(side=tk.LEFT)
        tk.Entry(frame2, textvariable=self.output_pdf, state='readonly', width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame2, text="保存...", command=self.select_output_pdf).pack(side=tk.LEFT)

        # 框架3：页面大小选择
        frame3 = tk.Frame(self.root, pady=5)
        frame3.pack(fill=tk.X, padx=20)

        tk.Label(frame3, text="页面大小：", width=12).pack(side=tk.LEFT)
        tk.Radiobutton(frame3, text="A4", variable=self.page_size, value="A4").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame3, text="Letter", variable=self.page_size, value="letter").pack(side=tk.LEFT, padx=10)

        # 框架4：进度和开始按钮
        frame4 = tk.Frame(self.root, pady=10)
        frame4.pack(fill=tk.X, padx=20)

        self.progress_label = tk.Label(frame4, text="准备就绪", fg="blue")
        self.progress_label.pack(side=tk.LEFT, expand=True)

        self.start_button = tk.Button(frame4, text="开始转换", command=self.start_conversion, bg="#4CAF50", fg="white")
        self.start_button.pack(side=tk.RIGHT, padx=10)

    def select_image_folder(self):
        folder = filedialog.askdirectory(title="选择图片所在文件夹")
        if folder:
            self.image_folder.set(folder)

    def select_output_pdf(self):
        # 默认文件名：output.pdf，默认路径：图片文件夹
        initial_dir = self.image_folder.get() or "."
        file = filedialog.asksaveasfilename(
            title="保存PDF文件",
            initialdir=initial_dir,
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file:
            self.output_pdf.set(file)

    def start_conversion(self):
        # 检查路径
        if not self.image_folder.get():
            messagebox.showerror("错误", "请选择图片文件夹！")
            return
        if not self.output_pdf.get():
            messagebox.showerror("错误", "请选择PDF保存路径！")
            return

        # 禁用按钮，防止重复点击
        self.start_button.config(state=tk.DISABLED, bg="#cccccc")
        self.progress_label.config(text="开始转换...")
        self.root.update_idletasks()  # 刷新UI

        # 执行转换
        try:
            convert_images_to_pdf(
                image_folder=self.image_folder.get(),
                output_pdf=self.output_pdf.get(),
                page_size=self.page_size.get(),
                progress_callback=self.update_progress
            )
            messagebox.showinfo("成功", f"PDF已生成：\n{self.output_pdf.get()}")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败：{str(e)}")
        finally:
            # 恢复按钮状态
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")

    def update_progress(self, text):
        self.progress_label.config(text=text)
        self.root.update_idletasks()  # 刷新UI

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPdfApp(root)
    root.mainloop()