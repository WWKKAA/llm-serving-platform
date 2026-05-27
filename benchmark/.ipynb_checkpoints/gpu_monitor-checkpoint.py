import csv
import subprocess
import time
from datetime import datetime


OUTPUT_FILE = "benchmark/gpu_metrics.csv"


def query_gpu():
    cmd = [
        "nvidia-smi",
        "--query-gpu=timestamp,name,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]

    result = subprocess.check_output(cmd, text=True)
    return result.strip()


def main(interval: float = 1.0):
    print(f"开始记录 GPU 指标，输出文件: {OUTPUT_FILE}")
    print("按 Ctrl+C 停止")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "local_time",
            "gpu_timestamp",
            "gpu_name",
            "gpu_util_percent",
            "memory_used_mb",
            "memory_total_mb",
            "power_w",
            "temperature_c",
        ])

        try:
            while True:
                line = query_gpu()
                parts = [item.strip() for item in line.split(",")]

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    *parts,
                ])
                f.flush()

                print(line)
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nGPU 监控结束")


if __name__ == "__main__":
    main(interval=1.0)