# dichromatic

画像を Lab 色空間で変換し、赤–緑の色差（`a*` 軸）を除去する Python プログラムです。オプションで青–黄の色差（`b*` 軸）を弱めることもできます。

## 処理内容

1. 入力画像を **CIELAB** 色空間に変換する
2. **`a*` を 0** にする（赤–緑の色差情報を捨てる）
3. `--half-b` 指定時は **`b*` を半分**にする（青–黄の彩度を弱める）
4. RGB 色空間に戻して書き出す

Lab 色空間の各軸は次のとおりです。

| 軸 | 意味 |
|----|------|
| `L*` | 明度 |
| `a*` | 緑 (−) ↔ 赤 (+) |
| `b*` | 青 (−) ↔ 黄 (+) |

このプログラムは `L*` と `b*`（および `--half-b` 時は `b*`/2）を保持し、`a*` だけを除去します。RGBA 画像の場合、アルファチャンネルはそのまま保持されます。

## 必要条件

- Python 3.9 以上（推奨）

## インストール

```bash
git clone <repository-url>
cd dichromatic
pip install -r requirements.txt
```

## 使い方

```bash
python dichromatic.py input.jpg
```

出力ファイル名を省略した場合、`input_dichromatic.jpg` として保存されます。

```bash
# 出力先を指定
python dichromatic.py input.jpg -o output.png

# b* を半分にする
python dichromatic.py input.jpg --half-b

# HEIC / HEIF も読み込み可能
python dichromatic.py photo.heic -o result.jpg --half-b
```

## オプション

```
usage: dichromatic.py [-h] [-o OUTPUT] [--half-b] input

positional arguments:
  input                 入力画像のパス (JPEG, PNG, HEIF, HEIC など)

options:
  -h, --help            ヘルプを表示
  -o, --output OUTPUT   出力画像のパス (省略時: <name>_dichromatic.<ext>)
  --half-b              a* を 0 にしたあと、b* を半分にする
```

## 対応形式

Pillow および [pillow-heif](https://pypi.org/project/pillow-heif/) が読み書きできる形式に対応しています。例:

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- HEIF / HEIC (`.heif`, `.heic`)
- WebP (`.webp`)
- その他 Pillow 対応形式

## 依存関係

- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)
- [pillow-heif](https://pypi.org/project/pillow-heif/)（HEIF / HEIC 読み込み用）

## ライセンス

[GNU General Public License v3.0](LICENSE)
