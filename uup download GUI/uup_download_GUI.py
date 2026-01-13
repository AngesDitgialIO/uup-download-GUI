import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import subprocess
import threading
import time

class UUPDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("UUP Dump 下载工具")
        self.root.geometry("1000x800")
        
        # 初始化变量
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.is_downloading = False
        self.builds = []
        self.languages = []  # 语言列表
        self.selected_build = None
        
        # 创建界面
        self.create_widgets()
        
        # 加载最新构建
        self.load_latest_builds()
    
    def create_widgets(self):
        # 创建滚动容器
        scrollable_frame = ttk.Frame(self.root)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(scrollable_frame)
        scrollbar = ttk.Scrollbar(scrollable_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和Scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建主框架并将其添加到Canvas中
        main_frame = ttk.Frame(canvas, padding="20")
        canvas.create_window((0, 0), window=main_frame, anchor=tk.NW)
        
        # 配置Canvas的滚动区域
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        main_frame.bind("<Configure>", configure_scroll_region)
        
        # 允许鼠标滚轮在Canvas上滚动
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        # 标题
        ttk.Label(main_frame, text="UUP Dump 自动下载工具", font=("Arial", 16)).pack(pady=10)
        
        # 构建选择
        build_frame = ttk.LabelFrame(main_frame, text="选择系统构建", padding="10")
        build_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(build_frame, text="最新构建:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.build_combobox = ttk.Combobox(build_frame, width=70, state="readonly")
        self.build_combobox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.build_combobox.bind("<<ComboboxSelected>>", self.on_build_selected)
        
        # 刷新按钮
        refresh_btn = ttk.Button(build_frame, text="刷新", command=self.load_latest_builds)
        refresh_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # 语言选择
        language_frame = ttk.LabelFrame(main_frame, text="选择语言", padding="10")
        language_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(language_frame, text="语言:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_combobox = ttk.Combobox(language_frame, width=70, state="readonly")
        self.language_combobox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.language_combobox.bind("<<ComboboxSelected>>", self.on_language_selected)  # 添加语言选择事件
        
        # 加载语言按钮
        self.load_language_btn = ttk.Button(language_frame, text="加载语言", command=self.load_languages, state="disabled")
        self.load_language_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # 下载路径选择
        path_frame = ttk.LabelFrame(main_frame, text="下载设置", padding="10")
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="下载路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.insert(0, self.download_path)
        self.path_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_path)
        browse_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # SKU版本选择
        sku_frame = ttk.LabelFrame(main_frame, text="SKU 版本选择", padding="10")
        sku_frame.pack(fill=tk.X, pady=10)
        
        self.sku_listbox = tk.Listbox(sku_frame, height=10, selectmode=tk.MULTIPLE)
        self.sku_listbox.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        sku_scrollbar = ttk.Scrollbar(sku_frame, orient=tk.VERTICAL, command=self.sku_listbox.yview)
        sku_scrollbar.grid(row=0, column=1, sticky=tk.NS, pady=5)
        self.sku_listbox.config(yscrollcommand=sku_scrollbar.set)
        
        # 全选/取消全选按钮
        sku_btn_frame = ttk.Frame(sku_frame)
        sku_btn_frame.grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(sku_btn_frame, text="全选", command=self.select_all_skus).pack(pady=5, fill=tk.X)
        ttk.Button(sku_btn_frame, text="取消全选", command=self.deselect_all_skus).pack(pady=5, fill=tk.X)
        
        # 虚拟升级版本选择
        self.virtual_editions = []
        self.virtual_editions_vars = {}
        
        virtual_frame = ttk.LabelFrame(main_frame, text="虚拟升级版本选择 (仅在选择第3种下载方式时生效)", padding="10")
        virtual_frame.pack(fill=tk.X, pady=10)
        
        # 注意：虚拟升级版本将在SKU加载后动态添加
        self.virtual_editions_label = ttk.Label(virtual_frame, text="请先选择SKU版本")
        self.virtual_editions_label.pack(anchor=tk.W, pady=5)
        
        self.virtual_editions_container = ttk.Frame(virtual_frame)
        self.virtual_editions_container.pack(fill=tk.X, pady=5)
        
        # 下载选项
        download_options_frame = ttk.LabelFrame(main_frame, text="下载选项", padding="10")
        download_options_frame.pack(fill=tk.X, pady=10)
        
        self.download_method = tk.IntVar(value=2)  # 默认选择第三种下载方式
        ttk.Radiobutton(download_options_frame, text="下载 UUP 文件集", variable=self.download_method, value=1).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(download_options_frame, text="下载并转换为 ISO 镜像文件", variable=self.download_method, value=2).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(download_options_frame, text="下载、添加虚拟升级版本并转换为 ISO 镜像文件", variable=self.download_method, value=3).pack(anchor=tk.W, pady=2)
        
        # 转换选项
        conversion_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="10")
        conversion_frame.pack(fill=tk.X, pady=10)
        
        self.include_updates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(conversion_frame, text="包括更新 (仅 Windows 转换程序)", variable=self.include_updates_var).pack(anchor=tk.W, pady=2)
        
        self.component_cleanup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(conversion_frame, text="运行组件清理 (仅 Windows 转换程序)", variable=self.component_cleanup_var).pack(anchor=tk.W, pady=2)
        
        self.netfx3_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(conversion_frame, text="集成 .NET Framework 3.5 (仅 Windows 转换程序)", variable=self.netfx3_var).pack(anchor=tk.W, pady=2)
        
        self.esd_compression_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(conversion_frame, text="使用固态压缩 (ESD)", variable=self.esd_compression_var).pack(anchor=tk.W, pady=2)
        
        # 自动操作选项
        auto_options_frame = ttk.LabelFrame(main_frame, text="自动操作选项", padding="10")
        auto_options_frame.pack(fill=tk.X, pady=10)
        
        self.auto_extract_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_options_frame, text="自动解压", variable=self.auto_extract_var).pack(anchor=tk.W, pady=2)
        
        self.auto_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_options_frame, text="自动运行 uup_download_windows.cmd", variable=self.auto_run_var).pack(anchor=tk.W, pady=2)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="准备就绪")
        self.status_label.pack(pady=10)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(button_frame, text="开始下载", command=self.start_download)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.run_existing_btn = ttk.Button(button_frame, text="运行已解压文件夹", command=self.run_existing_folder)
        self.run_existing_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 日志
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
    
    def on_build_selected(self, event):
        selected_index = self.build_combobox.current()
        if selected_index != -1:
            self.selected_build = self.builds[selected_index]
            self.load_language_btn.config(state="normal")
            self.log(f"选择了构建: {self.selected_build[0]}")
    
    def load_languages(self):
        if not self.selected_build:
            messagebox.showwarning("警告", "请先选择一个构建")
            return
        
        self.log("正在加载语言列表...")
        threading.Thread(target=self._load_languages_thread).start()
    
    def _load_languages_thread(self):
        try:
            build_name, build_id = self.selected_build
            build_url = f"https://uupdump.net/selectlang.php?id={build_id}"
            
            self.log(f"正在访问构建页面: {build_url}")
            response = requests.get(build_url)
            response.raise_for_status()  # 检查请求是否成功
            
            self.log(f"获取页面成功，状态码: {response.status_code}")
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找所有语言选项
            self.languages = []
            
            # 查找带有action="selectedition.php"的表单
            lang_form = soup.find("form", action="selectedition.php")
            
            if not lang_form:
                self.log("未找到语言选择表单")
                self.log("尝试查找所有表单:")
                all_forms = soup.find_all("form")
                for i, form in enumerate(all_forms):
                    self.log(f"表单 {i+1}: action={form.get('action')}")
                self.root.after(0, lambda: messagebox.showwarning("警告", "未找到语言选择表单"))
                return
            
            self.log("找到语言选择表单")
            
            # 在表单中查找select元素
            select_element = lang_form.find("select")
            if not select_element:
                self.log("在表单中未找到select元素")
                self.root.after(0, lambda: messagebox.showwarning("警告", "未找到语言选择下拉菜单"))
                return
            
            self.log("找到语言选择下拉菜单")
            
            # 获取select的名称
            select_name = select_element.get("name")
            if not select_name:
                self.log("select元素没有name属性")
                self.root.after(0, lambda: messagebox.showwarning("警告", "语言选择下拉菜单格式不正确"))
                return
            
            self.log(f"select元素名称: {select_name}")
            
            # 获取所有隐藏字段
            hidden_fields = lang_form.find_all("input", type="hidden")
            base_form_data = {}
            for field in hidden_fields:
                name = field.get("name")
                value = field.get("value")
                if name and value:
                    base_form_data[name] = value
            
            self.log(f"找到隐藏字段: {base_form_data}")
            
            # 提取所有选项
            options = select_element.find_all("option")
            self.log(f"找到 {len(options)} 个语言选项")
            
            for option in options:
                value = option.get("value")
                text = option.text.strip()
                
                if value and text and value != "None":  # 跳过空选项
                    # 为每种语言创建表单数据
                    lang_form_data = base_form_data.copy()
                    lang_form_data[select_name] = value
                    
                    self.languages.append((text, lang_form_data))
                    self.log(f"添加语言: {text} (值: {value})")
            
            # 更新界面
            self.root.after(0, self._update_language_combobox)
            self.log(f"加载完成，找到 {len(self.languages)} 种语言")
            
            # 如果没有找到语言，显示警告
            if not self.languages:
                self.log("未找到有效语言选项")
                self.root.after(0, lambda: messagebox.showwarning("警告", "未找到有效语言选项"))
            
        except requests.exceptions.RequestException as e:
            self.log(f"网络请求失败: {str(e)}")
            messagebox.showerror("错误", f"网络请求失败: {str(e)}")
        except Exception as e:
            self.log(f"加载语言失败: {str(e)}")
            import traceback
            self.log(f"详细错误信息: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载语言失败: {str(e)}")
    
    def _update_language_combobox(self):
        self.language_combobox['values'] = [lang[0] for lang in self.languages]
        if self.languages:
            self.language_combobox.current(0)
            # 自动加载SKU版本
            self.load_skus()
    
    def load_skus(self):
        if not self.languages:
            messagebox.showwarning("警告", "请先选择一种语言")
            return
        
        self.log("正在加载SKU版本...")
        threading.Thread(target=self._load_skus_thread).start()
    
    def _load_skus_thread(self):
        try:
            selected_lang_index = self.language_combobox.current()
            if selected_lang_index == -1:
                raise Exception("未选择语言")
            
            lang_name, form_data = self.languages[selected_lang_index]
            
            # 提交语言选择表单，获取SKU页面
            # 注意：应该使用GET请求，将参数作为URL参数传递，而不是POST请求
            versions_url = "https://uupdump.net/selectedition.php"
            response = requests.get(versions_url, params=form_data)
            response.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找所有SKU选项
            self.skus = []
            
            # 使用attrs字典来指定所有属性条件，避免参数传递问题
            # 注意：uupdump.net上的SKU复选框名称是edition[]而不是sku_*
            sku_checkboxes = soup.find_all(
                "input", 
                attrs={
                    "type": "checkbox",
                    "name": "edition[]"
                }
            )
            
            for checkbox in sku_checkboxes:
                # 获取SKU值
                sku_value = checkbox.get("value")
                # 获取SKU名称
                sku_name = checkbox.find_next("label").text.strip()
                # 构建SKU ID
                sku_id = f"edition[{sku_value}]"
                self.skus.append((sku_name, sku_id, sku_value))
            
            self.log(f"找到 {len(sku_checkboxes)} 个SKU复选框")
            
            # 更新界面
            self.root.after(0, self._update_sku_listbox)
            self.log(f"加载完成，找到 {len(self.skus)} 个SKU版本")
            
        except Exception as e:
            self.log(f"加载SKU版本失败: {str(e)}")
            messagebox.showerror("错误", f"加载SKU版本失败: {str(e)}")
    
    def _update_sku_listbox(self):
        # 清空现有列表
        self.sku_listbox.delete(0, tk.END)
        
        # 添加所有SKU选项
        for sku_name, sku_id, sku_value in self.skus:
            self.sku_listbox.insert(tk.END, sku_name)
        
        # 默认全选
        self.select_all_skus()
        
        # 加载虚拟升级版本
        self.load_virtual_editions()
    
    def select_all_skus(self):
        self.sku_listbox.select_set(0, tk.END)
    
    def deselect_all_skus(self):
        self.sku_listbox.selection_clear(0, tk.END)
    
    def load_virtual_editions(self):
        if not self.skus:
            self.log("没有SKU版本可加载虚拟升级版本")
            return
        
        self.log("正在加载虚拟升级版本...")
        threading.Thread(target=self._load_virtual_editions_thread).start()
    
    def _load_virtual_editions_thread(self):
        try:
            selected_sku_indices = self.sku_listbox.curselection()
            if not selected_sku_indices:
                self.log("没有选择任何SKU版本")
                self.root.after(0, lambda: self.virtual_editions_label.config(text="请选择SKU版本"))
                return
            
            # 获取第一个选择的SKU
            selected_sku_index = selected_sku_indices[0]
            sku_name, sku_id, sku_value = self.skus[selected_sku_index]
            
            # 获取语言选择信息
            selected_lang_index = self.language_combobox.current()
            if selected_lang_index == -1:
                raise Exception("未选择语言")
            
            lang_name, lang_form_data = self.languages[selected_lang_index]
            build_id = lang_form_data["id"]
            pack_value = lang_form_data.get("pack", "zh-cn")
            
            # 构建下载页面URL参数
            params = {
                "id": build_id,
                "pack": pack_value,
                "edition": sku_value,
                "download": "3"  # 使用第三种下载方式来获取虚拟升级版本
            }
            
            self.log(f"访问下载页面获取虚拟升级版本，参数: {params}")
            
            download_url = "https://uupdump.net/download.php"
            response = requests.get(download_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找虚拟升级版本复选框
            virtual_checkboxes = soup.find_all(
                "input",
                attrs={
                    "type": "checkbox",
                    "name": "virtualEditions[]"
                }
            )
            
            self.log(f"找到 {len(virtual_checkboxes)} 个虚拟升级版本")
            
            self.virtual_editions = []
            
            for checkbox in virtual_checkboxes:
                virtual_value = checkbox.get("value")
                virtual_label = checkbox.find_next("label")
                
                if virtual_value and virtual_label:
                    virtual_name = virtual_label.text.strip()
                    self.virtual_editions.append((virtual_name, virtual_value))
            
            # 更新界面
            self.root.after(0, self._update_virtual_editions)
            
        except Exception as e:
            self.log(f"加载虚拟升级版本失败: {str(e)}")
            import traceback
            self.log(f"详细错误信息: {traceback.format_exc()}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"加载虚拟升级版本失败: {str(e)}"))
    
    def _update_virtual_editions(self):
        # 清空现有控件
        for widget in self.virtual_editions_container.winfo_children():
            widget.destroy()
        
        if not self.virtual_editions:
            self.virtual_editions_label.config(text="未找到虚拟升级版本")
            return
        
        self.virtual_editions_label.config(text="可选择的虚拟升级版本:")
        
        # 添加虚拟升级版本复选框
        self.virtual_editions_vars = {}
        
        for i, (virtual_name, virtual_value) in enumerate(self.virtual_editions):
            var = tk.BooleanVar()
            self.virtual_editions_vars[virtual_value] = var
            
            checkbox = ttk.Checkbutton(
                self.virtual_editions_container,
                text=virtual_name,
                variable=var
            )
            checkbox.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
        
        # 添加全选/取消全选按钮
        virtual_btn_frame = ttk.Frame(self.virtual_editions_container)
        virtual_btn_frame.grid(row=(len(self.virtual_editions)+1)//2, column=0, columnspan=2, pady=10)
        
        ttk.Button(virtual_btn_frame, text="全选虚拟版本", command=self.select_all_virtual_editions).pack(side=tk.LEFT, padx=5)
        ttk.Button(virtual_btn_frame, text="取消全选虚拟版本", command=self.deselect_all_virtual_editions).pack(side=tk.LEFT, padx=5)
    
    def select_all_virtual_editions(self):
        for var in self.virtual_editions_vars.values():
            var.set(True)
    
    def deselect_all_virtual_editions(self):
        for var in self.virtual_editions_vars.values():
            var.set(False)
    
    def on_language_selected(self, event):
        selected_index = self.language_combobox.current()
        if selected_index != -1:
            self.log(f"手动选择了语言: {self.languages[selected_index][0]}")
            # 自动加载SKU版本
            self.load_skus()
    
    def load_latest_builds(self):
        self.log("正在加载最新构建...")
        threading.Thread(target=self._load_builds_thread).start()
    
    def _load_builds_thread(self):
        try:
            url = "https://uupdump.net"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找构建项目
            self.builds = []
            
            # 查找所有包含id参数的链接
            build_links = soup.find_all('a', href=lambda href: href and 'id=' in href)
            
            for link in build_links:
                href = link.get('href')
                text = link.text.strip()
                
                # 提取构建ID（应该是GUID格式）
                if 'id=' in href:
                    build_id = href.split('id=')[-1]
                    
                    # 检查是否为有效的GUID格式（包含连字符）
                    if '-' in build_id:
                        self.builds.append((text, build_id))
                    
                # 只添加前10个有效的构建
                if len(self.builds) >= 10:
                    break
            
            # 更新界面
            self.root.after(0, self._update_build_combobox)
            self.log(f"加载完成，找到 {len(self.builds)} 个有效的GUID格式构建")
            
            # 如果没有找到构建，显示详细信息
            if not self.builds:
                self.log(f"未找到有效的构建项目，共检查了 {len(build_links)} 个链接")
                for i, link in enumerate(build_links[:5]):
                    self.log(f"链接 {i+1}: {link.get('href')} - {link.text.strip()}")
                
        except Exception as e:
            self.log(f"加载构建失败: {str(e)}")
            import traceback
            self.log(f"详细错误信息: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载构建失败: {str(e)}")
    
    def _update_build_combobox(self):
        self.build_combobox['values'] = [build[0] for build in self.builds]
        if self.builds:
            self.build_combobox.current(0)
    
    def start_download(self):
        if self.is_downloading:
            return
        
        if not self.builds:
            messagebox.showwarning("警告", "请先加载构建列表")
            return
        
        selected_index = self.build_combobox.current()
        if selected_index == -1:
            messagebox.showwarning("警告", "请选择一个构建")
            return
        
        self.is_downloading = True
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.status_label.config(text="开始下载...")
        
        selected_build = self.builds[selected_index]
        threading.Thread(target=self._download_thread, args=(selected_build,)).start()
    
    def cancel_download(self):
        self.is_downloading = False
        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.status_label.config(text="已取消")
        self.log("下载已取消")
    
    def _download_thread(self, build):
        try:
            build_name, build_id = build
            self.log(f"开始下载构建: {build_name}")
            
            # 步骤1: 检查选择
            selected_lang_index = self.language_combobox.current()
            if selected_lang_index == -1:
                raise Exception("请先选择一种语言")
            
            selected_sku_indices = self.sku_listbox.curselection()
            if not selected_sku_indices:
                raise Exception("请至少选择一个SKU版本")
            
            # 步骤2: 获取选择的语言和SKU数据
            lang_name, lang_form_data = self.languages[selected_lang_index]
            self.log(f"选择的语言: {lang_name}")
            
            # 获取构建ID，确保下载表单包含必要的ID参数
            build_name, build_id = self.selected_build
            self.log(f"使用的构建ID: {build_id}")
            
            # 确保表单数据包含id参数
            if "id" not in lang_form_data:
                lang_form_data["id"] = build_id
                self.log("添加了缺失的id参数到表单数据中")
            
            selected_skus = [self.skus[i] for i in selected_sku_indices]
            selected_sku_names = [sku[0] for sku in selected_skus]
            self.log(f"选择的SKU版本: {', '.join(selected_sku_names)}")
            
            # 步骤3: 提交语言选择表单，获取SKU页面
            # 使用selectedition.php而不是get.php，与SKU加载保持一致
            versions_url = "https://uupdump.net/selectedition.php"
            self.log(f"提交语言选择，获取SKU页面")
            
            # 使用GET请求，与SKU加载保持一致
            response = requests.get(versions_url, params=lang_form_data)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 步骤4: 构建包含选择SKU的表单数据
            # 尝试多种方式查找下载表单
            download_form = soup.find("form", action="/download.php")
            
            if not download_form:
                # 尝试模糊匹配包含download.php的action
                download_form = soup.find("form", action=lambda action: action and "download.php" in action)
            
            if not download_form:
                # 尝试查找带有method="post"的表单
                download_form = soup.find("form", method="post")
            
            if not download_form:
                # 保存页面内容以便调试
                with open("sku_page_error.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                raise Exception("未找到下载表单，请查看保存的sku_page_error.html文件了解详情")
            
            # 获取基础表单数据
            form_data = {}
            
            # 首先添加lang_form_data中的所有数据，包括id参数
            form_data.update(lang_form_data)
            
            # 然后添加表单中的输入字段
            for input_field in download_form.find_all("input"):
                name = input_field.get("name")
                value = input_field.get("value")
                
                # 特殊处理edition字段：如果是隐藏字段且值为空，我们将在后面设置
                if name == "edition" and not value:
                    continue
                
                if name and value:
                    form_data[name] = value
            
            # 添加选择的SKU
            # 根据调试结果，我们需要：
            # 1. 为每个选中的SKU设置edition[]参数
            # 2. 设置edition参数（单个值，使用第一个选中的SKU）
            selected_sku_values = []
            for i in selected_sku_indices:
                sku_name, sku_id, sku_value = self.skus[i]
                selected_sku_values.append(sku_value)
            
            # 设置edition[]参数（复选框格式）
            form_data["edition[]"] = selected_sku_values
            
            # 设置edition参数（单个值）
            if selected_sku_values:
                form_data["edition"] = selected_sku_values[0]  # 使用第一个选中的SKU
                self.log(f"设置edition参数为: {selected_sku_values[0]}")
            
            # 添加选择的虚拟升级版本 (仅在选择第3种下载方式时)
            if self.download_method.get() == 3:
                selected_virtual_editions = []
                for virtual_value, var in self.virtual_editions_vars.items():
                    if var.get():
                        selected_virtual_editions.append(virtual_value)
                
                if selected_virtual_editions:
                    form_data["virtualEditions[]"] = selected_virtual_editions
                    self.log(f"选择的虚拟升级版本: {', '.join(selected_virtual_editions)}")
            
            # 添加下载选项
            form_data["download"] = str(self.download_method.get())
            form_data["includeUpdates"] = "1" if self.include_updates_var.get() else "0"
            form_data["componentCleanup"] = "1" if self.component_cleanup_var.get() else "0"
            form_data["netFx3"] = "1" if self.netfx3_var.get() else "0"
            form_data["esdCompression"] = "1" if self.esd_compression_var.get() else "0"
            
            # 根据用户建议，我们将使用内置浏览器进行下载
            # 这是最可靠的方法，可以避免复杂的表单提交和链接检测
            
            # 获取基本参数
            # 从selected_build获取build_id
            build_name, build_id = self.selected_build
            
            # 获取语言代码
            lang_code = lang_form_data.get("pack", "zh-cn")
            
            # 获取选择的SKU
            selected_sku_values = []
            for i in selected_sku_indices:
                sku_name, sku_id, sku_value = self.skus[i]
                selected_sku_values.append(sku_value)
            
            if not selected_sku_values:
                raise Exception("未选择有效的SKU版本")
            
            # 只使用第一个选中的SKU
            selected_sku_value = selected_sku_values[0]
            
            # 构建下载URL（根据用户提供的参考URL格式）
            download_url = "https://uupdump.net/get.php"
            
            # 构建GET参数
            get_params = {
                "id": build_id,
                "pack": lang_code,
                "edition": selected_sku_value,
                "download": str(self.download_method.get()),
                "includeUpdates": "1" if self.include_updates_var.get() else "0",
                "componentCleanup": "1" if self.component_cleanup_var.get() else "0",
                "netFx3": "1" if self.netfx3_var.get() else "0",
                "esdCompression": "1" if self.esd_compression_var.get() else "0"
            }
            
            # 如果用户选择了虚拟升级版本
            if self.download_method.get() == 3:
                # 只使用第一个选中的虚拟升级版本
                for virtual_value, var in self.virtual_editions_vars.items():
                    if var.get():
                        get_params["virtualEdition"] = virtual_value
                        break
            
            # 将参数转换为URL查询字符串
            import urllib.parse
            query_string = urllib.parse.urlencode(get_params)
            
            # 构建完整的下载URL
            full_download_url = f"{download_url}?{query_string}"
            
            # 使用内置浏览器打开下载页面
            self.log(f"使用默认浏览器打开下载页面: {full_download_url}")
            
            import webbrowser
            webbrowser.open(full_download_url)
            
            self.log("浏览器已打开，请在浏览器中完成下载")
            
            # 如果设置了自动解压和自动运行选项，提示用户下载完成后手动操作
            if self.auto_extract_var.get() or self.auto_run_var.get():
                messagebox.showinfo("提示", "下载页面已在浏览器中打开。\n下载完成后，请手动将文件解压到指定目录，并运行相关脚本。")
            
            # 跳过自动下载，由用户在浏览器中完成
            return
            
        except Exception as e:
            self.log(f"下载失败: {str(e)}")
            messagebox.showerror("错误", f"下载失败: {str(e)}")
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.cancel_btn.config(state="disabled"))
    
    def download_file(self, url, filename):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for data in response.iter_content(chunk_size=8192):
                if not self.is_downloading:
                    return
                    
                f.write(data)
                downloaded += len(data)
                progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda p=progress: self.status_label.config(text=f"下载进度: {int(p)}%"))
        
        self.log(f"文件下载完成: {filename}")
    
    def extract_file(self, zip_path, extract_path):
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
        
        # 验证文件是否是有效的zip文件
        if not zipfile.is_zipfile(zip_path):
            # 获取文件的前几个字节，查看文件类型
            with open(zip_path, 'rb') as f:
                header = f.read(100)
                
            # 尝试获取文件内容的前几行
            with open(zip_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_preview = f.read(500)
                
            raise Exception(f"File is not a zip file. First 100 bytes: {header!r}. Content preview: {content_preview!r}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            for i, file in enumerate(file_list):
                if not self.is_downloading:
                    return
                    
                zip_ref.extract(file, extract_path)
                progress = (i + 1) / total_files * 100
                
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda p=progress: self.status_label.config(text=f"解压进度: {int(p)}%"))
        
        self.log(f"文件解压完成，解压到: {extract_path}")
    
    def run_script(self, script_path, working_dir):
        if not os.path.exists(script_path):
            self.log(f"脚本文件不存在: {script_path}")
            return
        
        try:
            # 运行脚本
            process = subprocess.Popen(
                [script_path], 
                cwd=working_dir, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时读取输出
            while process.poll() is None and self.is_downloading:
                output = process.stdout.readline()
                if output:
                    self.log(output.strip())
                
                error = process.stderr.readline()
                if error:
                    self.log(f"错误: {error.strip()}")
                
                time.sleep(0.1)
            
            self.log(f"脚本运行完成，返回代码: {process.returncode}")
            
        except Exception as e:
            self.log(f"运行脚本失败: {str(e)}")
    
    def run_existing_folder(self):
        # 允许用户选择已经解压好的UUP文件夹
        folder_path = filedialog.askdirectory(title="选择已解压的UUP文件夹")
        
        if not folder_path:
            return
        
        self.log(f"选择的文件夹: {folder_path}")
        
        # 检查文件夹中是否存在uup_download_windows.cmd脚本
        cmd_path = os.path.join(folder_path, "uup_download_windows.cmd")
        
        if not os.path.exists(cmd_path):
            # 尝试查找其他可能的脚本文件
            possible_scripts = []
            for filename in os.listdir(folder_path):
                if filename.endswith(".cmd") or filename.endswith(".bat"):
                    possible_scripts.append(filename)
            
            if possible_scripts:
                # 使用第一个找到的脚本文件
                cmd_path = os.path.join(folder_path, possible_scripts[0])
                self.log(f"未找到uup_download_windows.cmd，使用找到的第一个脚本: {possible_scripts[0]}")
            else:
                messagebox.showerror("错误", "在所选文件夹中未找到.cmd或.bat脚本文件")
                return
        
        # 运行脚本
        self.log(f"开始运行脚本: {cmd_path}")
        self.is_downloading = True
        
        # 禁用相关按钮
        self.run_existing_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        # 在新线程中运行脚本，避免阻塞GUI
        threading.Thread(target=self._run_existing_script, args=(cmd_path, folder_path)).start()
        
    def _run_existing_script(self, script_path, working_dir):
        try:
            # 运行脚本
            process = subprocess.Popen(
                [script_path], 
                cwd=working_dir, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时读取输出
            while process.poll() is None and self.is_downloading:
                output = process.stdout.readline()
                if output:
                    self.log(output.strip())
                
                error = process.stderr.readline()
                if error:
                    self.log(f"错误: {error.strip()}")
                
                time.sleep(0.1)
            
            if self.is_downloading:
                self.log(f"脚本运行完成，返回代码: {process.returncode}")
                messagebox.showinfo("完成", "脚本运行完成")
            else:
                self.log("脚本运行被取消")
                messagebox.showinfo("取消", "脚本运行已被取消")
            
        except Exception as e:
            self.log(f"运行脚本失败: {str(e)}")
            messagebox.showerror("错误", f"运行脚本失败: {str(e)}")
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.run_existing_btn.config(state="normal"))
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.cancel_btn.config(state="disabled"))
            self.root.after(0, lambda: self.status_label.config(text="准备就绪"))
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: self.log_text.insert(tk.END, f"[{timestamp}] {message}\n"))
        self.root.after(0, lambda: self.log_text.see(tk.END))

if __name__ == "__main__":
    root = tk.Tk()
    app = UUPDownloader(root)
    root.mainloop()
