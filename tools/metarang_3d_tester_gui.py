#!/usr/bin/env python3
"""MetaRang 3D Local Tester GUI (MR-3D-EXEC-V5.0) - Supports Dual-Track & 12 Categories."""
import json
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_PATH / "scripts"))

from analyze_3d_model import (
    analyze_model_directory,
    detect_asset_type_from_labels,
    fetch_github_issue,
    parse_issue_body,
    render_markdown_report,
)


class MetaRangTesterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MetaRang 3D Model Tester V5.0 | ابزار تست محلی ۱۲ دسته تخصصی")
        self.geometry("960x720")
        self.configure(bg="#0F172A")
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Header.TLabel", background="#0F172A", foreground="#2DD4BF", font=("Tahoma", 13, "bold"))

        ttk.Label(
            self,
            text="🌐 ابزار تست محلی مدل‌های سه‌بعدی متارنگ (V5.0 — ۱۲ دسته، RPM و Unity 6)",
            style="Header.TLabel",
        ).pack(pady=(14, 8))

        frame = tk.Frame(self, bg="#1E293B", padx=16, pady=14)
        frame.pack(fill="x", padx=18, pady=6)

        # Track Selection
        self.track_var = tk.StringVar(value="issue-backed")
        tk.Label(frame, text="مسیر ارسال (Track):", bg="#1E293B", fg="#F8FAFC", font=("Tahoma", 9, "bold")).grid(row=0, column=0, sticky="w")
        rb_frame = tk.Frame(frame, bg="#1E293B")
        rb_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 10))
        tk.Radiobutton(rb_frame, text="مسیر ۱: سفارش رسمی با لینک ایشو (v1/v2)", variable=self.track_var, value="issue-backed", bg="#1E293B", fg="#E2E8F0", selectcolor="#0F172A", font=("Tahoma", 9)).pack(side="left", padx=(0, 16))
        tk.Radiobutton(rb_frame, text="مسیر ۲: توسعه شخصی شهروند بدون ایشو (derivative-config.json)", variable=self.track_var, value="self-initiated", bg="#1E293B", fg="#E2E8F0", selectcolor="#0F172A", font=("Tahoma", 9)).pack(side="left")

        # Model Directory
        tk.Label(frame, text="مسیر دایرکتوری مدل:", bg="#1E293B", fg="#F8FAFC", font=("Tahoma", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.dir_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.dir_var, width=80, font=("Consolas", 10), bg="#0F172A", fg="#F8FAFC", insertbackground="white").grid(row=3, column=0, padx=(0, 8), pady=(0, 10))
        tk.Button(frame, text="انتخاب پوشه...", command=self._browse_dir, bg="#0F766E", fg="white", font=("Tahoma", 9, "bold"), relief="flat", padx=12, pady=4).grid(row=3, column=1, pady=(0, 10))

        # Issue URL (for Track 1)
        tk.Label(frame, text="لینک ایشو گیت‌هاب (فقط برای مسیر ۱):", bg="#1E293B", fg="#F8FAFC", font=("Tahoma", 9, "bold")).grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.issue_var = tk.StringVar(value="https://github.com/iranpsc/Model3d-Metaverse-Rang/issues/1")
        tk.Entry(frame, textvariable=self.issue_var, width=80, font=("Consolas", 10), bg="#0F172A", fg="#F8FAFC", insertbackground="white").grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.write_json_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="تولید خودکار product-detail.json داخل پوشه مدل", variable=self.write_json_var, bg="#1E293B", fg="#CBD5E1", selectcolor="#0F172A", font=("Tahoma", 9)).grid(row=6, column=0, sticky="w")

        self.run_btn = tk.Button(frame, text="🚀 اجرای تحلیل و تست V5.0", command=self._start_analysis, bg="#2563EB", fg="white", font=("Tahoma", 10, "bold"), relief="flat", padx=18, pady=7)
        self.run_btn.grid(row=6, column=1, sticky="e")

        self.status_lbl = tk.Label(self, text="آماده بررسی مدل...", bg="#0F172A", fg="#94A3B8", font=("Tahoma", 10, "bold"))
        self.status_lbl.pack(pady=(6, 4))

        self.output_box = scrolledtext.ScrolledText(self, wrap="word", font=("Consolas", 10), bg="#020617", fg="#E2E8F0", padx=12, pady=12)
        self.output_box.pack(fill="both", expand=True, padx=18, pady=(4, 16))

    def _browse_dir(self):
        sel = filedialog.askdirectory(title="انتخاب دایرکتوری مدل")
        if sel:
            self.dir_var.set(sel)

    def _start_analysis(self):
        d = self.dir_var.get().strip()
        track = self.track_var.get()
        issue_url = self.issue_var.get().strip()
        if not d or not Path(d).is_dir():
            messagebox.showerror("خطا", "مسیر دایرکتوری مدل معتبر نیست.")
            return
        if track == "issue-backed" and not issue_url:
            messagebox.showerror("خطا", "برای مسیر ۱، لینک ایشو گیت‌هاب الزامی است.")
            return

        self.run_btn.config(state="disabled")
        self.status_lbl.config(text="در حال اجرای تحلیل پلاگین‌محور V5.0...", fg="#38BDF8")
        self.output_box.delete("1.0", tk.END)
        threading.Thread(target=self._worker, args=(Path(d), track, issue_url), daemon=True).start()

    def _worker(self, model_dir: Path, track: str, issue_url: str):
        try:
            issue_spec, issue_num, asset_type = {}, None, ""
            ref = "Track 2 (Self-Initiated)"
            if track == "issue-backed":
                data = fetch_github_issue(issue_url, token=os.environ.get("GITHUB_TOKEN"))
                issue_spec = parse_issue_body(data.get("body", ""))
                issue_num = data.get("number")
                asset_type = detect_asset_type_from_labels(data.get("labels", []), data.get("title", ""))
                ref = issue_url

            passed, checks, detail = analyze_model_directory(
                model_dir=model_dir,
                issue_spec=issue_spec,
                asset_type=asset_type,
                track=track,
                issue_number=issue_num,
                github_actor="local-gui-tester",
                repo_root=BASE_PATH,
            )
            if self.write_json_var.get() and detail:
                (model_dir / "product-detail.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            report = render_markdown_report(passed, checks, detail, model_dir, ref)
            self.after(0, self._done, passed, report)
        except Exception as exc:
            self.after(0, self._err, str(exc))

    def _done(self, passed: bool, report: str):
        self.run_btn.config(state="normal")
        self.status_lbl.config(
            text="✅ PASS — مدل آماده ارسال PR است!" if passed else "❌ FAIL — قبل از Push موارد زیر را اصلاح کنید.",
            fg="#4ADE80" if passed else "#F87171",
        )
        self.output_box.insert(tk.END, report)

    def _err(self, msg: str):
        self.run_btn.config(state="normal")
        self.status_lbl.config(text="⚠️ خطا در اجرا", fg="#FBBF24")
        self.output_box.insert(tk.END, f"ERROR:\n{msg}\n")


if __name__ == "__main__":
    MetaRangTesterApp().mainloop()
