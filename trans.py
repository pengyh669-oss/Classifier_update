# simple_transcribe.py
import os
import whisper


# 移除了 subprocess 和 tempfile，因为转录脚本不需要转换音频格式

def main():
    print("开始转录recordings目录中的音频文件...")

    # 检查目录
    if not os.path.exists("recordings"):
        print("错误: 找不到recordings目录")
        return

    # 1. 🌟 修改点：从查找 '.webm' 改为查找 '.wav' 文件
    files = [f for f in os.listdir("recordings") if f.endswith('.wav')]

    if not files:
        print("错误: 没有找到.wav文件")

        # 提示用户检查 Flask 后端运行状态和 FFmpeg 转换
        print("请确认 Flask 后端已正确运行，且音频文件已成功转换为 .wav 格式。")
        return

    print(f"找到 {len(files)} 个WAV文件")

    # 加载模型
    print("加载Whisper模型...")
    # 注意：如果您的计算机性能有限，可以尝试更小的模型，如 "base.en" 或 "tiny"
    model = whisper.load_model("large-v2")

    # 创建输出目录
    os.makedirs("translation", exist_ok=True)

    # 按学号_姓名分组文件
    from collections import defaultdict
    student_files = defaultdict(list)
    for filename in files:
        parts = filename.split("_")
        if len(parts) >= 2:
            student_key = f"{parts[0]}_{parts[1]}"
        else:
            student_key = "未知学生"
        student_files[student_key].append(filename)

    print(f"共识别出 {len(student_files)} 个学生的录音\n开始转录...\n")

    for student_key, student_file_list in student_files.items():
        output_file = f"translation/{student_key}.txt"
        print(f"--- 正在处理学生: {student_key} ({len(student_file_list)} 个文件) ---")

        with open(output_file, "w", encoding="utf-8") as f:
            for i, filename in enumerate(student_file_list, 1):
                print(f"  [{i}/{len(student_file_list)}] 正在处理文件: {filename}")

                filepath = os.path.join("recordings", filename)

                try:
                    result = model.transcribe(filepath, language="zh")
                    text = result["text"].strip()

                    if text:
                        f.write(f"文件: {filename}\n")
                        f.write(f"转录结果: {text}\n")
                        f.write("-" * 40 + "\n\n")

                        print(f"    ✓ 成功转录: {text[:60]}...")
                    else:
                        f.write(f"文件: {filename}\n")
                        f.write("转录结果: 结果为空或为静音\n")
                        f.write("-" * 40 + "\n\n")
                        print("    ✗ 失败: 结果为空或静音")

                except Exception as e:
                    error_msg = str(e)
                    f.write(f"文件: {filename}\n")
                    f.write(f"错误: 转录失败 - {error_msg}\n")
                    f.write("-" * 40 + "\n\n")
                    print(f"    ✗ 失败: {error_msg[:80]}")

        print(f"  → 已保存: {output_file}\n")

    print("\n完成！转录结果保存在 translation/ 目录下")


if __name__ == "__main__":
    main()