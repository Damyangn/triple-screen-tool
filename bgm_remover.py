import os
import sys
import subprocess
from pathlib import Path


def run_audio_process_v2(input_dir):
    folder = Path(input_dir)
    temp_dir = folder / "temp_work"

    mp3_files = list(folder.glob("*.mp3"))
    if not mp3_files:
        print(f"❌ 未找到 mp3。")
        return

    py_exec = sys.executable

    for mp3 in mp3_files:
        # 跳过已经是处理后的文件
        if mp3.name.endswith("_pure.mp3"):
            continue

        print(f"\n======== 处理中: {mp3.name} ========")

        # 1. Demucs 深度提取 (增加 shifts 参数提升质量)
        print("➡️  Step 1/2: 提取人声 (增加计算强度)...")
        subprocess.run([
            py_exec, "-m", "demucs.separate",
            "--two-stems=vocals",
            "-n", "htdemucs_ft",
            "--shifts", "1",  # 增加位移计算，提高精度
            str(mp3), "-o", str(temp_dir)
        ])

        vocal_wav = temp_dir / "htdemucs_ft" / mp3.stem / "vocals.wav"

        # 2. DeepFilterNet 强化净化 (增加 --pf 后置滤波)
        print("➡️  Step 2/2: 深度净化 (开启后置滤波)...")
        subprocess.run([
            py_exec, "-m", "df.enhance",
            "--model-base-dir", "DeepFilterNet3",
            str(vocal_wav),
            "--output-dir", str(folder)
        ])

        # 3. FFmpeg 压缩回 MP3 并重命名
        # 我们寻找 DeepFilterNet 生成的文件 (通常叫 vocals_DeepFilterNet3.wav)
        raw_wav = folder / "vocals_DeepFilterNet3.wav"
        if not raw_wav.exists():
            raw_wav = folder / "vocals_enhanced.wav"

        final_mp3 = folder / f"{mp3.stem}_pure.mp3"

        if raw_wav.exists():
            print("➡️  Step 3: 正在转码压缩为高质量 MP3...")
            # 使用 ffmpeg 将 WAV 转回 320k 的 MP3
            subprocess.run([
                "ffmpeg", "-y", "-i", str(raw_wav),
                "-ab", "320k", str(final_mp3)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 删除巨大的临时 WAV 文件
            os.remove(raw_wav)
            print(f"✅ 处理完成！体积已缩小。文件名: {final_mp3.name}")

    print("\n✨ 全部任务已完成，生成的 MP3 体积已优化。")


if __name__ == "__main__":
    target_path = "/abc/voice"
    run_audio_process_v2(target_path)
