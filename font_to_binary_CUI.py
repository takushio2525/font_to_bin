import os
from PIL import Image, ImageDraw, ImageFont


def generate_binary_from_dot_font(text, font_path, size):
    """
    指定されたドットフォントを使い、文字をバイナリ行列に変換します。
    (GUI版からプレビュー画像生成部分を除いたCUI版)
    """
    if not os.path.exists(font_path):
        # フォントファイルが見つからない場合はエラーを発生させる
        raise FileNotFoundError(f"フォントファイルが見つかりません: {font_path}")

    output_size = (size, size)
    font = ImageFont.truetype(font_path, size=size)

    image = Image.new("1", output_size, 0)
    draw = ImageDraw.Draw(image)

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
    except AttributeError:
        left, top, right, bottom = draw.textsize(text, font=font)
        bbox = (left, top, right, bottom)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if text_width == 0 or text_height == 0:
        return None

    x_offset = (size - text_width) // 2 - bbox[0]
    y_offset = (size - text_height) // 2 - bbox[1]

    draw.text((x_offset, y_offset), text, font=font, fill=1)

    binary_matrix = []
    for y in range(size):
        row = [image.getpixel((x, y)) for x in range(size)]
        binary_matrix.append(row)

    return binary_matrix


def format_c_array(matrices):
    """
    バイナリ行列のリストをC言語の配列形式の文字列にフォーマットします。
    """
    if not matrices:
        return ""

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

    return result_string


def main():
    """
    CUIアプリケーションのメインループ
    """
    # --- フォントパスの定義 ---
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path_16 = os.path.join(script_dir, "DotGothic16-Regular.ttf")
        font_path_8 = os.path.join(script_dir, "misaki_gothic_2nd.ttf")
        # フォントファイルの存在チェック
        if not os.path.exists(font_path_16) or not os.path.exists(font_path_8):
            print(
                "エラー: 必要なフォントファイル (DotGothic16-Regular.ttf, misaki_gothic_2nd.ttf) が見つかりません。")
            print("スクリプトと同じディレクトリに配置してください。")
            return
    except NameError:
        # __file__ が定義されていない環境（例: 一部のインタラクティブ環境）のためのフォールバック
        print("エラー: スクリプトのパスを特定できません。")
        print("フォントファイル (DotGothic16-Regular.ttf, misaki_gothic_2nd.ttf) をカレントディレクトリに配置してください。")
        font_path_16 = "DotGothic16-Regular.ttf"
        font_path_8 = "misaki_gothic_2nd.ttf"

    while True:
        print("\n--- モードを選択してください ---")
        print("1: 単一文字変換")
        print("2: 文字列変換")
        print("q: 終了")
        mode = input("モード番号を入力してください: ").strip()

        if mode.lower() == 'q' or mode == 'ｑ':
            print("アプリケーションを終了します。")
            break
        elif mode == '1' or mode == '１':
            # --- 単一文字モード ---
            while True:
                char_input = input("変換する文字を1文字入力してください: ").strip()
                if len(char_input) == 1:
                    break
                print("エラー: 1文字だけ入力してください。")

            print("\n--- 16x16 (DotGothic16) ---")
            matrix_16 = generate_binary_from_dot_font(
                char_input, font_path_16, 16)
            if matrix_16:
                print(format_c_array([matrix_16]))

            print("\n--- 8x8 (Misaki Gothic) ---")
            matrix_8 = generate_binary_from_dot_font(
                char_input, font_path_8, 8)
            if matrix_8:
                print(format_c_array([matrix_8]))

        elif mode == '2' or mode == '２':
            # --- 文字列モード ---
            str_input = input("変換する文字列を入力してください: ").strip()
            if not str_input:
                print("エラー: 文字列が空です。")
                continue

            # 16x16
            print("\n--- 16x16 (DotGothic16) ---")
            matrices_16 = []
            for char in str_input:
                matrix = generate_binary_from_dot_font(char, font_path_16, 16)
                if matrix:
                    matrices_16.append(matrix)
            if matrices_16:
                print(format_c_array(matrices_16))

            # 8x8
            print("\n--- 8x8 (Misaki Gothic) ---")
            matrices_8 = []
            for char in str_input:
                matrix = generate_binary_from_dot_font(char, font_path_8, 8)
                if matrix:
                    matrices_8.append(matrix)
            if matrices_8:
                print(format_c_array(matrices_8))
        else:
            print("エラー: 無効なモードです。「1」、「2」、または「q」を入力してください。")


if __name__ == "__main__":
    main()
