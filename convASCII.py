import os
from PIL import Image, ImageDraw, ImageFont

# conv_ASCII関数で定義された文字セット
# A-Z (0-25), a-z (26-51), 0-9 (52-61), ! (62), ? (63)
CHARACTER_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?"


def generate_binary_from_dot_font(text, font_path, size):
    """
    指定されたドットフォントを使い、文字をバイナリ行列に変換します。
    フォントに文字が存在しない場合は、すべて0の行列を返します。
    """
    if not os.path.exists(font_path):
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

    # フォントにグリフ（文字の形）が含まれているかチェック
    if text_width == 0 or text_height == 0:
        # 含まれていない場合は空の（全て0の）行列を返す
        return [[0] * size for _ in range(size)]

    x_offset = (size - text_width) // 2 - bbox[0]
    y_offset = (size - text_height) // 2 - bbox[1]

    draw.text((x_offset, y_offset), text, font=font, fill=1)

    binary_matrix = []
    for y in range(size):
        row = [image.getpixel((x, y)) for x in range(size)]
        binary_matrix.append(row)

    return binary_matrix


def format_c_3d_array(array_name, matrices, size):
    """
    バイナリ行列のリストを、C言語の3次元配列形式の文字列にフォーマットします。
    """
    if not matrices:
        return ""

    # 配列の定義を開始
    result_string = f"const uint8_t {array_name}[{len(matrices)}][{size}][{size}] = {{\n"

    # 各文字の2D配列を生成
    for char_index, matrix in enumerate(matrices):
        result_string += f"    // {CHARACTER_SET[char_index]}\n"
        result_string += "    {\n"

        for i, row in enumerate(matrix):
            row_str = ", ".join(map(str, row))
            result_string += f"        {{{row_str}}}"
            if i < len(matrix) - 1:
                result_string += ",\n"
            else:
                result_string += "\n"

        result_string += "    }"
        if char_index < len(matrices) - 1:
            result_string += ",\n\n"
        else:
            result_string += "\n"

    result_string += "};"
    return result_string


def main():
    """
    フォントデータをC言語の配列としてファイルに出力するメイン関数
    """
    output_filename = "array.c"
    print(f"8x8フォント配列を {output_filename} に出力します...")

    # --- フォントパスの定義 ---
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path_8 = os.path.join(script_dir, "misaki_gothic_2nd.ttf")

        if not os.path.exists(font_path_8):
            print(
                "エラー: 必要なフォントファイル (misaki_gothic_2nd.ttf) が見つかりません。")
            print("スクリプトと同じディレクトリに配置してください。")
            return
    except NameError:
        print("エラー: スクリプトのパスを特定できません。")
        print("フォントファイル (misaki_gothic_2nd.ttf) をカレントディレクトリに配置してください。")
        font_path_8 = "misaki_gothic_2nd.ttf"

    # --- 8x8配列の生成 ---
    matrices_8 = []
    for char in CHARACTER_SET:
        matrix = generate_binary_from_dot_font(char, font_path_8, 8)
        matrices_8.append(matrix)

    # C言語の配列形式にフォーマット
    array_string = format_c_3d_array("font_data_8", matrices_8, 8)

    # --- ファイルへの書き込み ---
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("#include <stdint.h>\n\n")
            f.write("// --- 8x8 Font Data (Misaki Gothic) ---\n")
            f.write(array_string)
            f.write("\n")
        print(f"\n生成が完了しました。'{output_filename}' を確認してください。")
    except IOError as e:
        print(f"エラー: ファイルの書き込みに失敗しました: {e}")


if __name__ == "__main__":
    main()
