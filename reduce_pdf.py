"""origin フォルダの PDF を圧縮して reduced フォルダに出力する。"""
import sys
from pathlib import Path

import pymupdf

BASE = Path(__file__).resolve().parent
SRC = BASE / "origin"
DST = BASE / "reduced"

# 圧縮レベル: (この dpi を超える画像を, この dpi に縮小, JPEG 品質)
PRESETS = {
    "low":    (200, 150, 85),  # 画質優先
    "medium": (150, 120, 75),  # 標準
    "high":   (100,  96, 60),  # 容量優先
}


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def reduce(src, dst, preset):
    threshold, target, quality = PRESETS[preset]
    doc = pymupdf.open(src)
    doc.rewrite_images(dpi_threshold=threshold, dpi_target=target, quality=quality)
    try:
        doc.subset_fonts()
    except Exception:
        pass
    doc.scrub(metadata=False, xml_metadata=False, thumbnails=True, reset_fields=False,
              reset_responses=False, attached_files=False, clean_pages=True,
              embedded_files=False, hidden_text=False, javascript=False,
              redactions=False, remove_links=False)
    doc.save(dst, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True,
             clean=True, use_objstms=1)
    doc.close()


def main():
    preset = sys.argv[1] if len(sys.argv) > 1 else "medium"
    if preset not in PRESETS:
        print(f"圧縮レベルは {', '.join(PRESETS)} のいずれかを指定してください")
        return 1

    SRC.mkdir(exist_ok=True)
    DST.mkdir(exist_ok=True)
    pdfs = sorted(p for p in SRC.rglob("*") if p.suffix.lower() == ".pdf")
    if not pdfs:
        print(f"{SRC} に PDF がありません")
        return 0

    print(f"圧縮レベル: {preset}\n")
    total_before = total_after = 0
    for src in pdfs:
        rel = src.relative_to(SRC)
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        before = src.stat().st_size
        try:
            reduce(src, dst, preset)
        except Exception as e:
            print(f"[失敗] {rel}: {e}")
            continue
        after = dst.stat().st_size
        if after >= before:
            # 圧縮で逆に大きくなった場合は元ファイルをそのままコピー
            dst.write_bytes(src.read_bytes())
            after = before
            note = "（削減できなかったため元のまま）"
        else:
            note = ""
        total_before += before
        total_after += after
        rate = (1 - after / before) * 100 if before else 0
        print(f"{rel}: {human(before)} -> {human(after)} ({rate:.0f}% 削減){note}")

    if total_before:
        rate = (1 - total_after / total_before) * 100
        print(f"\n合計: {human(total_before)} -> {human(total_after)} ({rate:.0f}% 削減)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
