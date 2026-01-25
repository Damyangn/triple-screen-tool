import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

# 并行数量
MAX_WORKERS = 3
VIDEO_DIR = "/Volumes/640-KESU/Vedio"

def make_triple_screen_final(input_path):
    output_path = input_path.replace(".mp4", "_3screen_1080p.mp4")

    if os.path.exists(output_path):
        print(f"⚠️ 跳过: {os.path.basename(output_path)}")
        return

    print(f"🔄 处理中: {os.path.basename(input_path)}")

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-filter_complex",
        (
            # 1. 核心修复：缩放后直接复制成 3 份，并直接命名为 left, mid, right
            # 这样就不需要中间的翻转步骤了
            "[0:v]scale=-1:1080,split=3[left][mid][right];"

            # 2. 直接把这三份一模一样的拼起来
            "[left][mid][right]hstack=3,"

            # 3. 强制拉伸宽度到 1920
            "scale=1920:1080"
        ),
        # 视频编码 (Mac 硬件加速)
        "-c:v", "h264_videotoolbox",

        # ⚠️ 关键调整：改为 2000k，避免生成 4GB 的巨大文件
        "-b:v", "5000k",

        "-allow_sw", "1",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        # 保持静默模式 (不输出日志)
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        print(f"✅ 完成: {os.path.basename(output_path)}")
    except subprocess.CalledProcessError:
        print(f"❌ 失败: {os.path.basename(input_path)}")

if __name__ == "__main__":
    mp4_files = [
        os.path.join(VIDEO_DIR, f)
        for f in os.listdir(VIDEO_DIR)
        if f.endswith(".mp4") and "_3screen" not in f
    ]

    # 打印一下要处理的文件数量
    print(f"📂 扫描到 {len(mp4_files)} 个文件，开始处理...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(make_triple_screen_final, mp4_files)

    print("🎉 全部搞定！")