import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os


def generate_binary_from_dot_font(text, font_path, size):
    """
    指定されたドットフォントを使い、文字をバイナリ行列に変換します。
    アンチエイリアスを無効にし、各ピクセルの色で0/1を判断します。

    Args:
        text (str): 変換したい文字。
        font_path (str): 使用するフォントファイルのパス。
        size (int): フォントのサイズ (8または16)。

    Returns:
        tuple: (バイナリデータの2次元リスト, Pillowのプレビュー画像オブジェクト) または (None, None)
    """
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"フォントファイルが見つかりません: {font_path}")

    output_size = (size, size)
    font = ImageFont.truetype(font_path, size=size)

    # モノクロモード('1')で画像を作成し、アンチエイリアスなしで描画
    image = Image.new("1", output_size, 0)  # 0:黒
    draw = ImageDraw.Draw(image)

    # 文字の描画位置を中央に調整
    try:
        # Pillow 10.0.0以降
        bbox = draw.textbbox((0, 0), text, font=font)
    except AttributeError:
        # Pillow 10.0.0より前
        left, top, right, bottom = draw.textsize(text, font=font)
        bbox = (left, top, right, bottom)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if text_width == 0 or text_height == 0:
        return None, None

    x_offset = (size - text_width) // 2 - bbox[0]
    y_offset = (size - text_height) // 2 - bbox[1]

    draw.text((x_offset, y_offset), text, font=font, fill=1)  # 1:白

    # 画像のピクセルから直接バイナリ行列を生成
    binary_matrix = []
    for y in range(size):
        row = []
        for x in range(size):
            pixel_value = image.getpixel((x, y))
            row.append(pixel_value)  # '1'モードなので、値は既に0か1
        binary_matrix.append(row)

    # プレビュー画像生成
    # '1'モードから'L'モードに変換し、0/1を0/255にマッピングしてからリサイズ
    preview_image = image.convert("L").point(lambda i: i * 255)
    preview_image = preview_image.resize((160, 160), Image.Resampling.NEAREST)

    return binary_matrix, preview_image, image


class FontToBinApp:
    """
    フォント to バイナリ変換のGUIアプリケーションクラス
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Font to Binary Converter")
        self.root.geometry("800x650")  # 少し大きめにサイズ調整

        # --- フォントパスの定義 ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path_16 = os.path.join(
            script_dir, "DotGothic16-Regular.ttf")
        self.font_path_8 = os.path.join(script_dir, "misaki_gothic_2nd.ttf")

        # --- タブの作成 ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- タブ1: 単一文字変換 ---
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='単一文字変換')
        self.create_single_char_tab(self.tab1)

        # --- タブ2: 文字列変換 ---
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='文字列変換')
        self.create_string_tab(self.tab2)

    def create_single_char_tab(self, parent):
        """単一文字変換タブのUIを作成する"""
        # --- 変数の定義 ---
        self.char_to_convert = tk.StringVar(value="A")
        self.char_to_convert.trace_add("write", self.on_single_char_change)

        # --- GUIウィジェットの作成と配置 ---
        input_frame = tk.Frame(parent, padx=10, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="変換する文字:").grid(
            row=0, column=0, sticky="w", pady=2)
        char_entry = tk.Entry(
            input_frame, textvariable=self.char_to_convert, width=5)
        char_entry.grid(row=0, column=1, sticky="w")

        results_frame = tk.Frame(parent, padx=10, pady=5)
        results_frame.pack(fill="both", expand=True)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(1, weight=1)

        # --- 16x16 結果表示 ---
        frame_16 = tk.LabelFrame(
            results_frame, text="16x16 (DotGothic16)", padx=10, pady=10)
        frame_16.grid(row=0, column=0, sticky="nsew", padx=5)
        frame_16.grid_columnconfigure(0, weight=1)

        self.preview_canvas_16 = tk.Canvas(
            frame_16, width=160, height=160, bg="white", relief="sunken", borderwidth=1)
        self.preview_canvas_16.pack(pady=5)

        self.result_text_16 = tk.Text(
            frame_16, height=10, relief="sunken", borderwidth=1, font=("Courier", 9))
        self.result_text_16.pack(fill="both", expand=True, pady=5)
        copy_button_16 = tk.Button(
            frame_16, text="コピー", command=lambda: self.copy_to_clipboard(self.result_text_16))
        copy_button_16.pack(pady=(0, 5))

        # --- 8x8 結果表示 ---
        frame_8 = tk.LabelFrame(
            results_frame, text="8x8 (Misaki Gothic)", padx=10, pady=10)
        frame_8.grid(row=0, column=1, sticky="nsew", padx=5)
        frame_8.grid_columnconfigure(0, weight=1)

        self.preview_canvas_8 = tk.Canvas(
            frame_8, width=160, height=160, bg="white", relief="sunken", borderwidth=1)
        self.preview_canvas_8.pack(pady=5)

        self.result_text_8 = tk.Text(
            frame_8, height=10, relief="sunken", borderwidth=1, font=("Courier", 9))
        self.result_text_8.pack(fill="both", expand=True, pady=5)
        copy_button_8 = tk.Button(
            frame_8, text="コピー", command=lambda: self.copy_to_clipboard(self.result_text_8))
        copy_button_8.pack(pady=(0, 5))

        self.root.after(100, self.update_single_char_results)

    def create_string_tab(self, parent):
        """文字列変換タブのUIを作成する"""
        # --- スクロール可能な領域を作成 ---
        main_canvas = tk.Canvas(parent)
        v_scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(
                scrollregion=main_canvas.bbox("all")
            )
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=v_scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # --- これ以降のウィジェットは scrollable_frame を親にする ---
        container = scrollable_frame

        # --- 変数の定義 ---
        self.string_to_convert = tk.StringVar(value="ABC")
        self.string_to_convert.trace_add("write", self.on_string_change)

        # --- GUIウィジェットの作成と配置 ---
        input_frame = tk.Frame(container, padx=10, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="変換する文字列:").grid(
            row=0, column=0, sticky="w", pady=2)
        string_entry = tk.Entry(
            input_frame, textvariable=self.string_to_convert, width=40)
        string_entry.grid(row=0, column=1, sticky="we")
        input_frame.grid_columnconfigure(1, weight=1)

        # --- 16x16 結果表示 ---
        frame_16 = tk.LabelFrame(
            container, text="16x16 (DotGothic16)", padx=10, pady=10)
        frame_16.pack(fill="x", expand=True, padx=10, pady=5)

        preview_frame_16 = tk.Frame(frame_16)
        preview_frame_16.pack(fill="x", pady=5)
        self.str_preview_canvas_16 = tk.Canvas(
            preview_frame_16, height=160, bg="white", relief="sunken", borderwidth=1)
        x_scrollbar_16 = tk.Scrollbar(
            preview_frame_16, orient="horizontal", command=self.str_preview_canvas_16.xview)
        self.str_preview_canvas_16.configure(xscrollcommand=x_scrollbar_16.set)
        x_scrollbar_16.pack(side="bottom", fill="x")
        self.str_preview_canvas_16.pack(side="top", fill="x", expand=True)

        self.str_result_text_16 = tk.Text(
            frame_16, height=10, relief="sunken", borderwidth=1, font=("Courier", 9))
        self.str_result_text_16.pack(fill="both", expand=True, pady=5)
        copy_button_16 = tk.Button(
            frame_16, text="コピー", command=lambda: self.copy_to_clipboard(self.str_result_text_16))
        copy_button_16.pack(pady=(0, 5))

        # --- 8x8 結果表示 ---
        frame_8 = tk.LabelFrame(
            container, text="8x8 (Misaki Gothic)", padx=10, pady=10)
        frame_8.pack(fill="x", expand=True, padx=10, pady=5)

        preview_frame_8 = tk.Frame(frame_8)
        preview_frame_8.pack(fill="x", pady=5)
        self.str_preview_canvas_8 = tk.Canvas(
            preview_frame_8, height=160, bg="white", relief="sunken", borderwidth=1)
        x_scrollbar_8 = tk.Scrollbar(
            preview_frame_8, orient="horizontal", command=self.str_preview_canvas_8.xview)
        self.str_preview_canvas_8.configure(xscrollcommand=x_scrollbar_8.set)
        x_scrollbar_8.pack(side="bottom", fill="x")
        self.str_preview_canvas_8.pack(side="top", fill="x", expand=True)

        self.str_result_text_8 = tk.Text(
            frame_8, height=10, relief="sunken", borderwidth=1, font=("Courier", 9))
        self.str_result_text_8.pack(fill="both", expand=True, pady=5)
        copy_button_8 = tk.Button(
            frame_8, text="コピー", command=lambda: self.copy_to_clipboard(self.str_result_text_8))
        copy_button_8.pack(pady=(0, 5))

        self.root.after(100, self.update_string_results)

    # --- イベントハンドラ ---
    def on_single_char_change(self, *args):
        self.update_single_char_results()

    def on_string_change(self, *args):
        self.update_string_results()

    # --- 単一文字処理 ---
    def update_single_char_results(self):
        text = self.char_to_convert.get()
        if not text or len(text) > 1:
            self.clear_single_char_results()
            return
        self.update_font_results(
            text, self.preview_canvas_16, self.result_text_16, self.font_path_16, 16)
        self.update_font_results(
            text, self.preview_canvas_8, self.result_text_8, self.font_path_8, 8)

    # --- 文字列処理 ---
    def update_string_results(self):
        text = self.string_to_convert.get()
        if not text:
            self.clear_string_results()
            return
        self.update_string_font_results(
            text, self.str_preview_canvas_16, self.str_result_text_16, self.font_path_16, 16)
        self.update_string_font_results(
            text, self.str_preview_canvas_8, self.str_result_text_8, self.font_path_8, 8)

    # --- 共通ロジック ---
    def update_font_results(self, text, canvas, text_widget, font_path, size):
        try:
            matrix, preview, _ = generate_binary_from_dot_font(
                text, font_path, size)
            if matrix:
                self.update_preview(canvas, preview)
                self.update_result_text(text_widget, [matrix])
        except FileNotFoundError as e:
            self.clear_single_char_results()
            messagebox.showerror("エラー", e)
        except Exception:
            self.clear_single_char_results()

    def update_string_font_results(self, text, canvas, text_widget, font_path, size):
        matrices = []
        images = []
        try:
            for char in text:
                matrix, _, raw_image = generate_binary_from_dot_font(
                    char, font_path, size)
                if matrix:
                    matrices.append(matrix)
                    images.append(raw_image)

            if matrices:
                self.update_result_text(text_widget, matrices)
                # プレビュー画像を連結して表示
                total_width = sum(img.width for img in images)
                combined_image = Image.new('L', (total_width, size))
                x_offset = 0
                for img in images:
                    combined_image.paste(img, (x_offset, 0))
                    x_offset += img.width

                preview_image = combined_image.convert(
                    "L").point(lambda i: i * 255)
                preview_image = preview_image.resize(
                    (total_width * (160//size), 160), Image.Resampling.NEAREST)
                self.update_string_preview(canvas, preview_image)

        except FileNotFoundError as e:
            self.clear_string_results()
            messagebox.showerror("エラー", e)
        except Exception:
            self.clear_string_results()

    def copy_to_clipboard(self, text_widget):
        text_to_copy = text_widget.get("1.0", "end-1c")
        if text_to_copy:
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            messagebox.showinfo("コピー完了", "クリップボードにコピーしました。")

    def update_preview(self, canvas, image):
        photo = ImageTk.PhotoImage(image)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo

    def update_string_preview(self, canvas, image):
        photo = ImageTk.PhotoImage(image)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo
        canvas.config(scrollregion=canvas.bbox("all"))

    def update_result_text(self, text_widget, matrices):
        if not matrices:
            return

        is_3d = len(matrices) > 1
        result_string = ""

        for char_index, matrix in enumerate(matrices):
            if is_3d:
                result_string += "    {\n"

            for i, row in enumerate(matrix):
                row_str = ", ".join(map(str, row))
                indent = "        " if is_3d else "    "
                result_string += f"{indent}{{{row_str}}}"
                if i < len(matrix) - 1:
                    result_string += ",\n"
                else:
                    result_string += "\n"

            if is_3d:
                result_string += "    }"
                if char_index < len(matrices) - 1:
                    result_string += ",\n"
                else:
                    # 最後のブロックの後には何も追加しない
                    pass

        text_widget.configure(state='normal')
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, result_string)
        text_widget.configure(state='disabled')

    def clear_single_char_results(self):
        self.preview_canvas_16.delete("all")
        self.result_text_16.configure(state='normal')
        self.result_text_16.delete("1.0", tk.END)
        self.result_text_16.configure(state='disabled')
        self.preview_canvas_8.delete("all")
        self.result_text_8.configure(state='normal')
        self.result_text_8.delete("1.0", tk.END)
        self.result_text_8.configure(state='disabled')

    def clear_string_results(self):
        self.str_preview_canvas_16.delete("all")
        self.str_result_text_16.configure(state='normal')
        self.str_result_text_16.delete("1.0", tk.END)
        self.str_result_text_16.configure(state='disabled')
        self.str_preview_canvas_8.delete("all")
        self.str_result_text_8.configure(state='normal')
        self.str_result_text_8.delete("1.0", tk.END)
        self.str_result_text_8.configure(state='disabled')


def main():
    """
    GUIアプリケーションを初期化し、メインループを開始します。
    """
    root = tk.Tk()
    app = FontToBinApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
