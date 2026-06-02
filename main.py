"""main.py — UI shell: chạy VideoSubFinder + OCR pipeline.

Phụ thuộc:  config.py  ocr.py
Thư viện:   watchdog, google-api-python-client, oauth2client, httplib2, cv2, psutil
"""
import os, re, time, datetime, subprocess, threading
from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import cv2, psutil
from PIL import Image, ImageTk

import config as C
import ocr

_vsf_proc: subprocess.Popen = None  # tham chiếu để kill VSF

# ── Logging (thread-safe) ─────────────────────────────────────────────────────
def log(msg: str):
    def _w():
        log_box.config(state="normal")
        log_box.insert(tk.END, f"{msg}\n")
        log_box.see(tk.END)
        log_box.config(state="disabled")
    root.after(0, _w)

# ── Watchdog: theo dõi RGBImages trong khi VSF chạy ──────────────────────────
class _RGBWatcher(FileSystemEventHandler):
    def __init__(self, total_td: datetime.timedelta, log_fn: Callable):
        self.total_td   = total_td
        self.log        = log_fn
        self.count      = 0
        self.start_wall = time.time()   # thời điểm bắt đầu giám sát

    def on_created(self, event):
        if event.is_directory: return
        self.count += 1
        name = os.path.basename(event.src_path)

        m = re.search(r"(\d{1,2})_(\d{2})_(\d{2})_(\d+)", name)
        if not m or not self.total_td.total_seconds():
            self.log(f"📷 [{self.count}] {name}")
            return
        try:
            cur = datetime.timedelta(
                hours=int(m[1]), minutes=int(m[2]),
                seconds=int(m[3]), microseconds=int(m[4][:6])
            )
            vid_rem = self.total_td - cur          # thời gian video còn lại
            pct     = min(100.0, cur / self.total_td * 100)

            # Ước tính thời gian thực còn lại dựa trên tốc độ xử lý
            elapsed_wall = time.time() - self.start_wall
            if pct > 0:
                est_total_wall = elapsed_wall / (pct / 100)
                eta_wall = max(0, est_total_wall - elapsed_wall)
                eta_td   = datetime.timedelta(seconds=int(eta_wall))
                eta_str  = _fmt_td(eta_td)
            else:
                eta_str = "--:--"

            total_str  = _fmt_td(self.total_td)
            cur_str    = _fmt_td(cur)
            vid_rem_str = _fmt_td(vid_rem)
            n = self.count

            self.log(f"📷 [{n}] {cur_str}/{total_str} | vid còn {vid_rem_str} | ETA {eta_str} ({pct:.1f}%)")
            root.after(0, lambda: (
                status.config(
                    text=f"VSF  {cur_str} / {total_str}  |  vid còn {vid_rem_str}  |  ETA {eta_str}  |  ảnh {n}  ({pct:.1f}%)"
                ),
                bar.config(value=pct),
            ))
        except Exception:
            pass


def _fmt_td(td: datetime.timedelta) -> str:
    """Timedelta → 'HH:MM:SS'."""
    total = max(0, int(td.total_seconds()))
    h, r  = divmod(total, 3600)
    m, s  = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _watch_rgb(path: str, duration: str, log_fn):
    """Chờ thư mục RGBImages rồi giám sát, log mỗi ảnh mới."""
    log_fn(f"⏳ Chờ VSF tạo thư mục output...")
    for i in range(30):           # chờ tối đa 30s
        if os.path.exists(path): break
        if i % 5 == 4:            # log mỗi 5s
            log_fn(f"⏳ Chờ RGBImages... ({i+1}s)")
        time.sleep(1)
    else:
        log_fn("❌ Không thấy thư mục RGBImages sau 30s."); return

    log_fn(f"👀 RGBImages xuất hiện — bắt đầu giám sát")

    try:
        parts = duration.split(":")
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        total = datetime.timedelta(hours=h, minutes=m, seconds=s)
    except (ValueError, IndexError):
        total = datetime.timedelta()

    obs = Observer()
    obs.schedule(_RGBWatcher(total, log_fn), path, recursive=True)
    obs.start()
    C.state.observer = obs

# ── Lấy thời lượng video bằng cv2 ────────────────────────────────────────────
def _video_duration(path: str) -> str:
    try:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 1
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        total = int(frames / fps)
        h, r = divmod(total, 3600)
        m, s = divmod(r, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "00:00:00"

# ── Chạy VideoSubFinder ───────────────────────────────────────────────────────
def run_vsf():
    global _vsf_proc
    cfg = C.load()
    vsf   = cfg["vsf_path"]
    video = video_var.get().strip()
    profile = profile_var.get().strip()
    profile_key = profile.lower().replace(", ", "_")
    crop = cfg["crop_profiles"].get(profile_key, {})

    if not video or not os.path.isfile(video):
        messagebox.showerror("Lỗi", "Chọn file video hợp lệ."); return

    # Kiểm tra đường dẫn VSF
    default_vsf = C.DEFAULT["vsf_path"]
    if vsf != default_vsf and not os.path.isfile(vsf):
        if messagebox.askyesno("Cấu hình", 
                              "Đường dẫn VideoSubFinder không hợp lệ hoặc chưa được chọn.\n"
                              "Bạn có muốn chuyển sang tab Settings để chọn lại không?"):
            nb.select(2) # Chuyển sang tab Settings
        return

    if not crop:
        messagebox.showerror("Lỗi",
            f"Không tìm thấy crop profile '{profile_key}'.\n"
            f"Các profile hiện có: {list(cfg['crop_profiles'].keys())}\n"
            f"Hãy chọn lại profile hoặc dùng ✨ Toạ độ để tạo mới."
        ); return

    # VSF xuất vào: <cùng thư mục video>/<tên video>_out/RGBImages
    # (tên thư mục là RGBImages; "RBG" chỉ xuất hiện trong tên file ảnh bên trong — typo của VSF)
    out_dir = str(Path(video).parent / (Path(video).stem + "_out"))
    rbg_dir = os.path.join(out_dir, "RGBImages")
    duration = _video_duration(video)
    log(f"▶ VideoSubFinder | {Path(video).name} | {duration}")
    log(f"📁 Output: {out_dir}")

    top    = crop.get("top",    0.0)
    bottom = crop.get("bottom", 0.0)
    left   = crop.get("left",   0.0)
    right  = crop.get("right",  1.0)

    log(f"✂️  Crop [{profile_key}]: te={top}  be={bottom}  le={left}  re={right}")

    # Ghi nhớ profile vừa dùng
    _cfg = C.load()
    _cfg["last_profile"] = profile_key
    C.save(_cfg)

    cmd = [
        vsf,
        "-c",              # clear dirs
        "-r",              # run search
        "-i",  video,
        "-o",  out_dir,
        "-te", str(top),
        "-be", str(bottom),
        "-le", str(left),
        "-re", str(right),
    ]

    log(f"🔧 Lệnh: {' '.join(cmd)}")

    C.state.stop_event.clear()   # reset flag trước khi chạy mới
    btn_vsf.config(state="disabled"); btn_vsf_stop.config(state="normal")

    def _go():
        global _vsf_proc
        threading.Thread(target=_watch_rgb, args=(rbg_dir, duration, log), daemon=True).start()
        _vsf_proc = subprocess.Popen(cmd)
        _vsf_proc.wait()
        _vsf_proc = None
        rbg_out = rbg_dir                                            # capture
        srt_out = os.path.join(out_dir, Path(video).stem + ".srt")  # SRT trong _out/
        stopped = C.state.stop_event.is_set()  # True nếu user bấm Dừng VSF

        def _vsf_done(was_stopped=stopped):
            btn_vsf.config(state="normal"); btn_vsf_stop.config(state="disabled")
            if was_stopped:
                status.config(text="⏹ VSF đã dừng.")
                log("⏹ VSF đã dừng — không chuyển tab.")
                return  # không chuyển tab, không auto OCR
            status.config(text="✅ VSF xong.")
            bar.config(value=100)
            log("✅ VSF xong.")
            images_var.set(rbg_out)
            srt_var.set(srt_out)
            nb.select(1)
            if auto_ocr_var.get():
                log("⚡ Tự động chạy OCR...")
                run_ocr()

        root.after(0, _vsf_done)
    threading.Thread(target=_go, daemon=True).start()

def stop_vsf():
    global _vsf_proc
    C.state.stop_event.set()   # đánh dấu bị dừng thủ công
    if _vsf_proc and _vsf_proc.poll() is None:
        try:
            parent = psutil.Process(_vsf_proc.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            pass
    btn_vsf.config(state="normal"); btn_vsf_stop.config(state="disabled")
    log("⏹ Đã dừng VSF.")

# ── Chạy OCR ─────────────────────────────────────────────────────────────────
def run_ocr():
    cfg = C.load()
    images_dir = images_var.get().strip()
    srt_out    = srt_var.get().strip()
    if not images_dir:
        messagebox.showerror("Lỗi", "Chọn thư mục ảnh."); return
    if not srt_out:
        messagebox.showerror("Lỗi", "Chọn đường dẫn file SRT."); return

    # Kiểm tra credentials.json
    cred = cfg.get("credentials_file", "credentials.json")
    if not os.path.isfile(cred):
        messagebox.showerror("Cấu hình", "Chưa chọn file credentials.json hoặc file không tồn tại.\nVui lòng kiểm tra lại trong tab Settings\nSau đó nhấn quay lại đây và nhấn 'Chạy OCR'."); return

    # Lấy folder_id từ config
    folder_id = cfg.get("folder_id", "").strip()
    C.state.folder_id = folder_id

    # Chỉ nhắc lần đầu chưa có token (chưa đăng nhập Google lần nào)
    if not os.path.exists(C.token_file()):
        if not messagebox.askokcancel(
            "Xác nhận tài khoản",
            "Đây là lần đầu chạy OCR hoặc token đã bị xoá.\n\n"
            "Trình duyệt sẽ mở để đăng nhập Google — hãy chọn đúng tài khoản\n"
            "đã dùng để tạo credentials.json.\n\n"
            "Tiếp tục?"
        ):
            return
            
    btn_ocr.config(state="disabled"); btn_stop.config(state="normal")
    status.config(text="OCR đang chạy...")

    def _progress(done, total):
        # Tính ETA
        eta_str = ""
        if done > 0 and total > done and C.state.t0:
            elapsed = time.time() - C.state.t0
            speed = done / elapsed  # ảnh/giây
            rem_files = total - done
            rem_sec = rem_files / speed
            
            m, s = divmod(int(rem_sec), 60)
            eta_str = f" (Còn lại ~{m:02d}:{s:02d})"

        root.after(0, lambda: (
            bar.config(value=done/total*100 if total else 0),
            status.config(text=f"OCR: {done}/{total}{eta_str}"),
        ))

    def _finish(path):
        root.after(0, lambda: (
            btn_ocr.config(state="normal"), btn_stop.config(state="disabled"),
            status.config(text="Hoàn thành!" if path else "Đã dừng."),
            (messagebox.showinfo("Xong", f"SRT: {path}") if path else None),
        ))

    ocr.run(images_dir, srt_out,
            cfg["delete_raw_texts"], cfg["delete_texts"],
            log, _progress, _finish)

def stop_ocr():
    C.state.stop_event.set()
    btn_ocr.config(state="normal"); btn_stop.config(state="disabled")
    log("⏹ Đã yêu cầu dừng.")

# ── CropSelector ─────────────────────────────────────────────────────────────
class CropSelector:
    """Cửa sổ kéo đường crop trực tiếp trên frame video."""

    SNAP = 12  # pixel trên canvas (dễ bắt hơn)

    def __init__(self, video_path: str, on_confirm):
        self.video_path  = video_path
        self.on_confirm  = on_confirm
        self.cap         = None
        self.photo       = None
        self.current_frame = 0
        self.total_frames  = 0
        self.vw = self.vh  = 0   # kích thước video gốc
        self.dw = self.dh  = 0   # kích thước frame hiển thị thực tế (sau scale)
        self.ox = self.oy  = 0   # offset (letterbox padding)
        # tọa độ 4 đường (pixel trên video gốc)
        self.top_y    = 0
        self.bottom_y = 0
        self.left_x   = 0
        self.right_x  = 0
        self.dragging = None

        self.win = tk.Toplevel(root)
        self.win.title("✨ Chọn vùng crop")
        self.win.geometry("1000x760")
        self.win.protocol("WM_DELETE_WINDOW", self._close)

        # Canvas
        self.canvas = tk.Canvas(self.win, bg="#111111", cursor="arrow")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>",        self._press)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Motion>",          self._hover)
        self.canvas.bind("<Configure>",       lambda e: self._show_frame())  # re-render khi resize

        # Param row
        pf = tk.Frame(self.win, bg="#222222"); pf.pack(fill=tk.X, pady=2)
        self.top_var    = tk.StringVar()
        self.bottom_var = tk.StringVar()
        self.left_var   = tk.StringVar()
        self.right_var  = tk.StringVar()
        for label, var, color in (
            ("Top",    self.top_var,    "#FFD700"),
            ("Bottom", self.bottom_var, "#00FFFF"),
            ("Left",   self.left_var,   "#00FF00"),
            ("Right",  self.right_var,  "#00FF00"),
        ):
            tk.Label(pf, text=f"{label}:", fg=color, bg="#222222",
                     font=("Consolas", 10, "bold")).pack(side=tk.LEFT, padx=4)
            tk.Entry(pf, textvariable=var, width=8, state="readonly",
                     font=("Consolas", 10, "bold"), bg="#333333", fg=color,
                     readonlybackground="#333333").pack(side=tk.LEFT, padx=1)
        ttk.Button(pf, text="✅ Xác nhận", command=self._confirm).pack(side=tk.LEFT, padx=14)

        # Lưu thành profile
        tk.Label(pf, text="│", fg="#555555", bg="#222222").pack(side=tk.LEFT, padx=4)
        tk.Label(pf, text="Lưu profile:", fg="#AAAAAA", bg="#222222",
                 font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(4, 2))
        self.profile_name_var = tk.StringVar(value="custom")
        tk.Entry(pf, textvariable=self.profile_name_var, width=12,
                 font=("Consolas", 10), bg="#333333", fg="#FFFFFF",
                 insertbackground="#FFFFFF").pack(side=tk.LEFT, padx=2)
        ttk.Button(pf, text="💾 Lưu", command=self._save_profile).pack(side=tk.LEFT, padx=4)

        # Hướng dẫn
        tk.Label(pf, text="Kéo đường để điều chỉnh vùng subtitle",
                 fg="#AAAAAA", bg="#222222", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=8)

        # Timeline row
        tf = tk.Frame(self.win); tf.pack(fill=tk.X, pady=2)
        self.slider = ttk.Scale(tf, orient="horizontal", command=self._seek)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.time_lbl = tk.Label(tf, text="00:00:00.000", font=("Consolas", 10))
        self.time_lbl.pack(side=tk.LEFT, padx=4)
        ttk.Button(tf, text="▶▶ +1s", width=7, command=self._ff1s).pack(side=tk.LEFT, padx=4)

        self.win.after(80, self._load)

    # ── Video loading ─────────────────────────────────────────────────────────
    def _load(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", f"Không mở được video:\n{self.video_path}")
            self.win.destroy(); return

        self.vw = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.vh = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.config(to=max(1, self.total_frames - 1))

        # Load đường từ profile đang chọn
        _cfg = C.load()
        _p   = _cfg["crop_profiles"].get(profile_var.get(), {})
        top_pct   = _p.get("top",    0.1426)
        bot_pct   = _p.get("bottom", 0.0102)
        left_pct  = _p.get("left",   0.0)
        right_pct = _p.get("right",  1.0)

        self.top_y    = int((1 - top_pct)  * self.vh)
        self.bottom_y = int((1 - bot_pct)  * self.vh)
        self.left_x   = int(left_pct       * self.vw)
        self.right_x  = int(right_pct      * self.vw)
        self._update_params()
        self._start_decode_worker()
        self._show_frame()

    # ── Frame display ─────────────────────────────────────────────────────────
    def _show_frame(self):
        if not self.cap or not self.cap.isOpened() or not self.vw: return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret: return

        self.win.update_idletasks()
        cw = max(self.canvas.winfo_width(),  400)
        ch = max(self.canvas.winfo_height(), 300)

        # Scale giữ tỉ lệ, canh giữa (letterbox)
        scale     = min(cw / self.vw, ch / self.vh)
        self.dw   = int(self.vw * scale)
        self.dh   = int(self.vh * scale)
        self.ox   = (cw - self.dw) // 2   # offset X
        self.oy   = (ch - self.dh) // 2   # offset Y

        resized   = cv2.resize(frame, (self.dw, self.dh))
        img       = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        # Paste lên background đen đúng kích thước canvas
        bg        = Image.new("RGB", (cw, ch), (17, 17, 17))
        bg.paste(img, (self.ox, self.oy))
        self.photo = ImageTk.PhotoImage(bg)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self._draw_lines()
        self._update_params()

        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        t   = datetime.datetime.min + datetime.timedelta(seconds=self.current_frame / fps)
        self.time_lbl.config(text=t.strftime("%H:%M:%S.%f")[:-3])

    def _draw_lines(self):
        if not self.dw or not self.vw: return
        sx = self.dw / self.vw
        sy = self.dh / self.vh

        # Tọa độ pixel trên canvas (có tính offset letterbox)
        cy_top    = self.oy + int(self.top_y    * sy)
        cy_bottom = self.oy + int(self.bottom_y * sy)
        cx_left   = self.ox + int(self.left_x   * sx)
        cx_right  = self.ox + int(self.right_x  * sx)

        x0 = self.ox; x1 = self.ox + self.dw
        y0 = self.oy; y1 = self.oy + self.dh

        self.canvas.delete("lines")
        kw = dict(tags="lines")

        # Vùng tô mờ bên ngoài crop (giúp user thấy rõ vùng sẽ xử lý)
        alpha_fill = "#1A1A3A"
        self.canvas.create_rectangle(x0, y0,   x1, cy_top,    fill=alpha_fill, outline="", **kw)
        self.canvas.create_rectangle(x0, cy_bottom, x1, y1,   fill=alpha_fill, outline="", **kw)
        self.canvas.create_rectangle(x0, cy_top, cx_left,  cy_bottom, fill=alpha_fill, outline="", **kw)
        self.canvas.create_rectangle(cx_right, cy_top, x1, cy_bottom, fill=alpha_fill, outline="", **kw)

        # 4 đường crop
        self.canvas.create_line(x0, cy_top,    x1, cy_top,    fill="#FFD700", width=2, **kw)
        self.canvas.create_line(x0, cy_bottom, x1, cy_bottom, fill="#00FFFF", width=2, **kw)
        self.canvas.create_line(cx_left,  y0, cx_left,  y1,   fill="#00FF00", width=2, **kw)
        self.canvas.create_line(cx_right, y0, cx_right, y1,   fill="#00FF00", width=2, **kw)

        # Nhãn các đường
        self.canvas.create_text(x0+36, cy_top    - 8, text="TOP",    fill="#FFD700", font=("Consolas",8,"bold"), **kw)
        self.canvas.create_text(x0+48, cy_bottom + 8, text="BOTTOM", fill="#00FFFF", font=("Consolas",8,"bold"), **kw)
        self.canvas.create_text(cx_left  + 22, y0+10, text="L", fill="#00FF00", font=("Consolas",8,"bold"), **kw)
        self.canvas.create_text(cx_right - 22, y0+10, text="R", fill="#00FF00", font=("Consolas",8,"bold"), **kw)

    # ── Mouse events ──────────────────────────────────────────────────────────
    def _canvas_to_video(self, cx, cy):
        """Canvas pixel → video pixel (trừ offset letterbox, chia scale)."""
        if not self.dw or not self.dh: return 0, 0
        vx = int((cx - self.ox) * self.vw / self.dw)
        vy = int((cy - self.oy) * self.vh / self.dh)
        return vx, vy

    def _nearest_line(self, cx, cy):
        """Tìm đường gần nhất theo tọa độ CANVAS pixel (sau offset)."""
        if not self.dw or not self.vw: return None
        sx = self.dw / self.vw
        sy = self.dh / self.vh
        cy_top    = self.oy + int(self.top_y    * sy)
        cy_bottom = self.oy + int(self.bottom_y * sy)
        cx_left   = self.ox + int(self.left_x   * sx)
        cx_right  = self.ox + int(self.right_x  * sx)
        t = self.SNAP
        if abs(cy - cy_top)    < t: return "top"
        if abs(cy - cy_bottom) < t: return "bottom"
        if abs(cx - cx_left)   < t: return "left"
        if abs(cx - cx_right)  < t: return "right"
        return None

    def _press(self, e):
        self.dragging = self._nearest_line(e.x, e.y)

    def _drag(self, e):
        if not self.dragging: return
        vx, vy = self._canvas_to_video(e.x, e.y)
        vx = max(0, min(vx, self.vw))
        vy = max(0, min(vy, self.vh))
        if   self.dragging == "top":    self.top_y    = min(vy, self.bottom_y - 1)
        elif self.dragging == "bottom": self.bottom_y = max(vy, self.top_y    + 1)
        elif self.dragging == "left":   self.left_x   = min(vx, self.right_x  - 1)
        elif self.dragging == "right":  self.right_x  = max(vx, self.left_x   + 1)
        self._draw_lines()
        self._update_params()

    def _release(self, e):
        self.dragging = None
        self.canvas.config(cursor="arrow")

    def _hover(self, e):
        line = self._nearest_line(e.x, e.y)
        self.canvas.config(cursor={
            "top":    "sb_v_double_arrow",
            "bottom": "sb_v_double_arrow",
            "left":   "sb_h_double_arrow",
            "right":  "sb_h_double_arrow",
        }.get(line, "arrow"))

    # ── Timeline ──────────────────────────────────────────────────────────────
    def _start_decode_worker(self):
        """Khởi động worker thread liên tục decode frame từ queue."""
        import queue
        self._seek_queue = queue.Queue(maxsize=2)  # chỉ giữ frame mới nhất
        self._seek_after = None

        def _worker():
            while True:
                frame_idx = self._seek_queue.get()
                if frame_idx is None:   # sentinel → thoát
                    break
                # Xả hết queue cũ, chỉ lấy frame mới nhất
                while not self._seek_queue.empty():
                    try: frame_idx = self._seek_queue.get_nowait()
                    except: break
                if frame_idx is None:
                    break
                if not self.cap or not self.cap.isOpened():
                    continue
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
                if ret:
                    self.win.after(0, lambda f=frame, i=frame_idx: self._render_frame(f, i))

        self._decode_thread = threading.Thread(target=_worker, daemon=True)
        self._decode_thread.start()

    def _seek(self, val):
        idx = int(float(val))
        self.current_frame = idx
        try:
            # non-blocking put: nếu đầy thì drop frame cũ
            self._seek_queue.put_nowait(idx)
        except Exception:
            try:
                self._seek_queue.get_nowait()
                self._seek_queue.put_nowait(idx)
            except Exception:
                pass


    def _render_frame(self, frame, frame_idx):
        """Nhận frame đã decode, render lên canvas (main thread)."""
        if not self.vw: return
        cw = max(self.canvas.winfo_width(),  400)
        ch = max(self.canvas.winfo_height(), 300)

        scale   = min(cw / self.vw, ch / self.vh)
        self.dw = int(self.vw * scale)
        self.dh = int(self.vh * scale)
        self.ox = (cw - self.dw) // 2
        self.oy = (ch - self.dh) // 2

        resized = cv2.resize(frame, (self.dw, self.dh))
        img     = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        bg      = Image.new("RGB", (cw, ch), (17, 17, 17))
        bg.paste(img, (self.ox, self.oy))
        self.photo = ImageTk.PhotoImage(bg)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self._draw_lines()
        self._update_params()

        fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 25
        t   = datetime.datetime.min + datetime.timedelta(seconds=frame_idx / (fps or 25))
        self.time_lbl.config(text=t.strftime("%H:%M:%S.%f")[:-3])

    def _ff1s(self):
        if not self.cap: return
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.current_frame = min(int(self.current_frame + fps), self.total_frames - 1)
        self.slider.set(self.current_frame)
        self._seek(self.current_frame)

    # ── Params ────────────────────────────────────────────────────────────────
    def _update_params(self):
        if not self.vw or not self.vh: return
        self.top_var.set(   f"{1 - self.top_y    / self.vh:.4f}")
        self.bottom_var.set(f"{(self.vh - self.bottom_y) / self.vh:.4f}")
        self.left_var.set(  f"{self.left_x  / self.vw:.4f}")
        self.right_var.set( f"{self.right_x / self.vw:.4f}")

    def _save_profile(self):
        name = self.profile_name_var.get().strip().lower().replace(" ", "_")
        if not name:
            messagebox.showwarning("Tên trống", "Nhập tên profile trước khi lưu.")
            return
        try:
            vals = {
                "top":    float(self.top_var.get()),
                "bottom": float(self.bottom_var.get()),
                "left":   float(self.left_var.get()),
                "right":  float(self.right_var.get()),
            }
        except ValueError:
            messagebox.showwarning("Chưa chọn", "Kéo ít nhất một đường trước khi lưu.")
            return

        cfg = C.load()
        is_new = name not in cfg["crop_profiles"]
        cfg["crop_profiles"][name] = vals
        C.save(cfg)

        # Cập nhật combobox và chọn profile vừa lưu
        new_values = list(C.load()["crop_profiles"].keys())
        combo_profile["values"] = new_values
        profile_var.set(name)
        _refresh_crop_label()

        action = "Đã thêm" if is_new else "Đã cập nhật"
        log(f"💾 {action} profile '{name}': top={vals['top']:.4f}  bottom={vals['bottom']:.4f}  left={vals['left']:.4f}  right={vals['right']:.4f}")

    def _confirm(self):
        try:
            self.on_confirm(
                top=float(self.top_var.get()),
                bottom=float(self.bottom_var.get()),
                left=float(self.left_var.get()),
                right=float(self.right_var.get()),
            )
        except ValueError:
            messagebox.showwarning("Chưa chọn", "Kéo ít nhất một đường trước khi xác nhận.")
            return
        self._close()

    def _close(self):
        if hasattr(self, "_seek_queue"):
            try: self._seek_queue.put_nowait(None)  # dừng worker
            except Exception: pass
        if self.cap: self.cap.release()
        self.win.destroy()


def open_crop_selector():
    video = video_var.get().strip()
    if not video or not os.path.isfile(video):
        video = filedialog.askopenfilename(
            filetypes=[("Video", "*.mp4 *.mkv *.avi *.mov")], title="Chọn video")
        if not video: return
        video_var.set(video)

    def _apply(top, bottom, left, right):
        try:
            cfg = C.load()
            cfg["crop_profiles"]["custom"] = {"top": top, "bottom": bottom,
                                              "left": left, "right": right}
            C.save(cfg)
            new_values = list(C.load()["crop_profiles"].keys())
            combo_profile["values"] = new_values
            profile_var.set("custom")
            _refresh_crop_label()
            log(f"✅ Crop lưu: top={top:.4f}  bottom={bottom:.4f}  left={left:.4f}  right={right:.4f}")
        except Exception as e:
            import traceback
            log(f"❌ Lỗi lưu crop: {e}\n{traceback.format_exc()}")

    CropSelector(video, _apply)


# ── UI ────────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("VSF OCR Tool")
root.geometry("720x520")
root.resizable(True, True)

# ─ Notebook tabs ─────────────────────────────────────────────────────────────
nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True, padx=8, pady=(6, 0))

# Ngăn việc tự động bôi đen các trường nhập liệu khi chuyển tab
def _on_tab_changed(_):
    nb.focus_set()
nb.bind("<<NotebookTabChanged>>", _on_tab_changed)

# Tab 1: VideoSubFinder
t1 = ttk.Frame(nb); nb.add(t1, text="① VideoSubFinder")
video_var   = tk.StringVar()
cfg0        = C.load()
_last       = cfg0.get("last_profile", "default")
# Fallback về "default" nếu profile đã bị xóa
if _last not in cfg0.get("crop_profiles", {}):
    _last = "default"
profile_var = tk.StringVar(value=_last)

ttk.Label(t1, text="File video:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
ttk.Entry(t1, textvariable=video_var, width=52).grid(row=0, column=1, padx=4)
ttk.Button(t1, text="…", width=3,
           command=lambda: video_var.set(filedialog.askopenfilename(
               filetypes=[("Video","*.mp4 *.mkv *.avi *.mov")])
           )).grid(row=0, column=2, padx=2)

ttk.Label(t1, text="Crop profile:").grid(row=1, column=0, sticky="w", padx=6)
combo_profile = ttk.Combobox(t1, textvariable=profile_var, width=20,
                              values=list(cfg0["crop_profiles"].keys()), state="readonly")
combo_profile.grid(row=1, column=1, sticky="w", padx=4)
ttk.Button(t1, text="✨ Toạ độ", width=10,
           command=open_crop_selector).grid(row=1, column=2, padx=2)

# ── Hiển thị tọa độ crop hiện tại ────────────────────────────────────────────
crop_info_var = tk.StringVar(value="—")
ttk.Label(t1, text="Tọa độ:").grid(row=2, column=0, sticky="w", padx=6)
ttk.Label(t1, textvariable=crop_info_var, foreground="#0055cc",
          font=("Consolas", 9)).grid(row=2, column=1, columnspan=2, sticky="w", padx=4)

def _refresh_crop_label(*_):
    p = profile_var.get()
    cfg = C.load()
    v = cfg["crop_profiles"].get(p)
    if v:
        crop_info_var.set(
            f"top={v['top']:.4f}  bottom={v['bottom']:.4f}  "
            f"left={v['left']:.4f}  right={v['right']:.4f}"
        )
    else:
        crop_info_var.set("—")

profile_var.trace_add("write", _refresh_crop_label)
_refresh_crop_label()   # hiển thị ngay khi khởi động

# ── Thư mục output (readonly, tự cập nhật theo video_var) ───────────────────
output_dir_var = tk.StringVar(value="—")
ttk.Label(t1, text="Output:").grid(row=3, column=0, sticky="w", padx=6)
ttk.Entry(t1, textvariable=output_dir_var, width=52, state="readonly",
          foreground="#666666").grid(row=3, column=1, columnspan=2, sticky="w", padx=4)

def _refresh_output_dir(*_):
    v = video_var.get().strip()
    if v and os.path.isfile(v):
        out = str(Path(v).parent / (Path(v).stem + "_out"))
        rgb = out + "/RGBImages"
        output_dir_var.set(rgb)
    else:
        output_dir_var.set("—")

video_var.trace_add("write", _refresh_output_dir)

btn_vsf      = ttk.Button(t1, text="▶ Chạy VSF",  command=run_vsf)
btn_vsf.grid(row=4, column=0, padx=6, pady=10)
btn_vsf_stop = ttk.Button(t1, text="⏹ Dừng VSF", command=stop_vsf, state="disabled")
btn_vsf_stop.grid(row=4, column=1, pady=10)

auto_ocr_var = tk.BooleanVar(value=True)
ttk.Checkbutton(t1, text="⚡ Tự động chạy OCR ngay sau khi VSF xong",
                variable=auto_ocr_var).grid(row=5, column=0, columnspan=3,
                                            sticky="w", padx=6, pady=(0, 4))

# Tab 2: OCR
t2 = ttk.Frame(nb); nb.add(t2, text="② OCR → SRT")
images_var = tk.StringVar()
srt_var    = tk.StringVar()

def check_images_folder(*_):
    path = images_var.get().strip()
    if path and os.path.isdir(path):
        try:
            count = 0
            for f in os.listdir(path):
                if f.lower().endswith(('.jpeg', '.jpg', '.png', '.bmp')):
                    count += 1
            log(f"📁 Đã chọn thư mục ảnh: {path}")
            log(f"ℹ️ Tìm thấy {count} ảnh trong thư mục này.")
        except Exception as e:
            log(f"⚠️ Không thể đọc thư mục ảnh: {e}")

images_var.trace_add("write", check_images_folder)

def _row(parent, r, label, var, pick_fn):
    ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=6, pady=4)
    ttk.Entry(parent, textvariable=var, width=52).grid(row=r, column=1, padx=4)
    ttk.Button(parent, text="…", width=3, command=pick_fn).grid(row=r, column=2, padx=2)

_row(t2, 0, "Thư mục ảnh:", images_var,
     lambda: images_var.set(filedialog.askdirectory()))

# Gợi ý bên dưới dòng path thư mục ảnh
ttk.Label(t2, text="Gợi ý: Chọn thư mục 'RGBImages' trong thư mục kết quả '_out' từ VideoSubFinder.",
          foreground="#888888", font=("Helvetica", 8)).grid(row=1, column=1, sticky="w", padx=4, pady=(0,4))

_row(t2, 2, "Lưu SRT:", srt_var,
     lambda: srt_var.set(filedialog.asksaveasfilename(
         defaultextension=".srt", filetypes=[("SRT","*.srt")])))

bf = ttk.Frame(t2); bf.grid(row=3, column=0, columnspan=3, pady=(5, 5))
btn_ocr  = ttk.Button(bf, text="▶ Chạy OCR",  command=run_ocr);  btn_ocr.pack(side="left", padx=6)
btn_stop = ttk.Button(bf, text="⏹ Dừng", command=stop_ocr, state="disabled"); btn_stop.pack(side="left")

# ── Tab 3: Settings ───────────────────────────────────────────────────────────
t3 = ttk.Frame(nb); nb.add(t3, text="⚙ Settings")

def _srow(r, label, var, pick_fn=None, hint=None, clear_btn=False):
    ttk.Label(t3, text=label).grid(row=r, column=0, sticky="w", padx=8, pady=5)
    ttk.Entry(t3, textvariable=var, width=48).grid(row=r, column=1, padx=4, sticky="ew")
    
    btn_f = ttk.Frame(t3)
    btn_f.grid(row=r, column=2, padx=2, sticky="w")
    
    if pick_fn:
        ttk.Button(btn_f, text="…", width=3, command=pick_fn).pack(side="left", padx=1)
    if clear_btn:
        ttk.Button(btn_f, text="✖", width=3, command=lambda: var.set("")).pack(side="left", padx=1)

    if hint:
        ttk.Label(t3, text=hint, foreground="#888888",
                  font=("Helvetica", 8)).grid(row=r+1, column=1, sticky="w", padx=4, pady=(0,2))

s_cfg = C.load()
s_folder_var  = tk.StringVar(value=s_cfg.get("folder_id", ""))
s_cred_var    = tk.StringVar(value=s_cfg.get("credentials_file", "credentials.json"))
s_vsf_var     = tk.StringVar(value=s_cfg.get("vsf_path", ""))
s_threads_var = tk.StringVar(value=str(s_cfg.get("threads", 20)))
s_del_raw_var = tk.BooleanVar(value=s_cfg.get("delete_raw_texts", False))
s_del_txt_var = tk.BooleanVar(value=s_cfg.get("delete_texts", False))
s_zip_raw_var = tk.BooleanVar(value=s_cfg.get("nen_raw_texts", False))

# Trace hiển thị đường dẫn tuyệt đối cho credentials
s_cred_abs_var = tk.StringVar()

def browse_drive_folder():
    import webbrowser
    from tkinter import simpledialog
    # Sử dụng AccountChooser làm "gate" để user chọn đúng tài khoản trước khi vào Drive
    url_gate = "https://accounts.google.com/AccountChooser?continue=https://drive.google.com/drive/my-drive"
    webbrowser.open(url_gate)
    
    url = simpledialog.askstring("Nhập link Folder Drive", 
                                "Trình duyệt đã mở trang chọn tài khoản.\n"
                                "1. Chọn đúng tài khoản khớp với credentials.json\n"
                                "2. Mở folder bạn muốn dùng trên Drive\n"
                                "3. Copy link trên thanh địa chỉ và dán vào đây:",
                                parent=root)
    if url:
        # Làm sạch URL: bỏ khoảng trắng và dấu xuyệt ở cuối
        url = url.strip().strip('/')
        # Regex tìm ID trong link Drive: folders/<ID> hoặc id=<ID>
        m = re.search(r"(?:folders/|id=)([a-zA-Z0-9_-]{28,})", url)
        if m:
            s_folder_var.set(m.group(1))
            log(f"📂 Đã trích xuất ID: {m.group(1)}")
        else:
            # Nếu không khớp regex, lấy đoạn cuối cùng của đường dẫn
            potential_id = url.split('/')[-1].split('?')[0].split('#')[0]
            if len(potential_id) >= 28:
                s_folder_var.set(potential_id)
                log(f"📂 Đã lấy ID: {potential_id}")
            else:
                messagebox.showwarning("Lỗi", "Không tìm thấy Folder ID hợp lệ trong link vừa dán.")

_srow(0, "Drive Folder ID:",    s_folder_var,
      pick_fn=browse_drive_folder, clear_btn=True,
      hint="Lấy từ URL Drive: drive.google.com/drive/folders/<ID>")

# --- credentials.json: ẩn cho tới khi user chọn file hợp lệ ---
_cred_label = ttk.Label(t3, text="credentials.json:")
_cred_label.grid(row=2, column=0, sticky="w", padx=8, pady=5)

_cred_entry = ttk.Entry(t3, textvariable=s_cred_var, width=48)

# Frame chứa nút Browse
_cred_btn_f = ttk.Frame(t3)
_cred_btn_f.grid(row=2, column=2, padx=2, sticky="w")

# Hint khi chưa chọn
_cred_hint = ttk.Label(t3, text="Tải từ Google Cloud Console → APIs & Services → Credentials",
                        foreground="#888888", font=("Helvetica", 8))
_cred_hint.grid(row=3, column=1, sticky="w", padx=4, pady=(0,2))

# Row 4: path hiện tại + trạng thái (ẩn mặc định)
_cred_path_label = ttk.Label(t3, text="Path hiện tại:", foreground="#0055cc")
_cred_path_entry = ttk.Entry(t3, textvariable=s_cred_abs_var, width=48,
                              state="readonly", foreground="#666666")
_cred_status = ttk.Label(t3, text="", foreground="#228B22", font=("Helvetica", 8))

def _show_cred_status():
    """Hiện ô path + dòng trạng thái xanh khi file hợp lệ."""
    _cred_entry.grid(row=2, column=1, padx=4, sticky="ew")
    _cred_path_label.grid(row=4, column=0, sticky="w", padx=20)
    _cred_path_entry.grid(row=4, column=1, padx=4, sticky="ew")
    _cred_status.grid(row=5, column=1, sticky="w", padx=4, pady=(0,2))

def _hide_cred_status():
    """Ẩn ô path + trạng thái."""
    _cred_entry.grid_forget()
    _cred_path_label.grid_forget()
    _cred_path_entry.grid_forget()
    _cred_status.grid_forget()

def _update_cred_display(*_):
    """Cập nhật hiển thị dựa trên trạng thái hiện tại của s_cred_var."""
    path = s_cred_var.get().strip()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    target_cred = os.path.join(root_dir, C.DEFAULT_CLIENT_SECRET)

    if path and os.path.isfile(path):
        abs_path = os.path.abspath(path)
        s_cred_abs_var.set(abs_path)
        _show_cred_status()
        if os.path.abspath(path) == os.path.abspath(target_cred):
            _cred_status.config(text="✔ Đã hợp lệ — file nằm tại thư mục dự án")
        else:
            _cred_status.config(text="✔ Đã chọn — file sẽ được copy vào dự án khi Lưu")
    elif path and os.path.isfile(target_cred):
        # Trường hợp path ngắn gọn (chỉ tên file) và file đã tồn tại ở root
        s_cred_abs_var.set(os.path.abspath(target_cred))
        _show_cred_status()
        _cred_status.config(text="✔ Đã hợp lệ — file nằm tại thư mục dự án")
    else:
        s_cred_abs_var.set("")
        _hide_cred_status()

def _browse_credentials():
    """Cho user chọn file, copy ngay vào dự án, cập nhật UI."""
    import shutil
    chosen = filedialog.askopenfilename(
        title="Chọn credentials.json",
        filetypes=[("JSON", "*.json")])
    if not chosen:
        return
    root_dir = os.path.dirname(os.path.abspath(__file__))
    target_cred = os.path.join(root_dir, C.DEFAULT_CLIENT_SECRET)
    # Copy nếu file ở nơi khác
    if os.path.abspath(chosen) != os.path.abspath(target_cred):
        try:
            shutil.copy2(chosen, target_cred)
            log(f"📋 Đã copy credentials.json vào thư mục dự án.")
        except Exception as e:
            log(f"❌ Không thể copy credentials: {e}")
            messagebox.showerror("Lỗi", f"Không thể copy file:\n{e}")
            return
    s_cred_var.set(C.DEFAULT_CLIENT_SECRET)
    _update_cred_display()

ttk.Button(_cred_btn_f, text="…", width=3, command=_browse_credentials).pack(side="left", padx=1)

# Khởi tạo: kiểm tra trạng thái ban đầu
_update_cred_display()


_srow(6, "VideoSubFinder path:", s_vsf_var,
      pick_fn=lambda: s_vsf_var.set(filedialog.askopenfilename(
          title="Chọn VideoSubFinder",
          filetypes=[("All Files", "*"), ("Executable", "*.exe;*.run;*")])),
      hint="Ví dụ: /workspaces/markdown-editor/VideoSubFinder/VideoSubFinderWXW.run")
_srow(8, "OCR threads:",        s_threads_var,
      hint="Số luồng xử lý song song (mặc định 20, tối đa ~50)")

# Checkboxes cho delete_raw_texts, delete_texts, nen_raw_texts
cb_frame = ttk.LabelFrame(t3, text="Tùy chọn dọn dẹp & Tối ưu hệ thống")
cb_frame.grid(row=10, column=0, columnspan=3, padx=8, pady=10, sticky="ew")

ttk.Checkbutton(cb_frame, text="Tự động xóa folder raw_texts (chứa file text thô từ OCR) sau khi chạy xong",
                variable=s_del_raw_var).pack(anchor="w", padx=6, pady=3)
ttk.Checkbutton(cb_frame, text="Tự động xóa folder texts (chứa file srt nhỏ đã dịch) sau khi chạy xong",
                variable=s_del_txt_var).pack(anchor="w", padx=6, pady=3)
ttk.Checkbutton(cb_frame, text="Tự động nén folder raw_texts thành file raw_texts.zip sau khi chạy xong",
                variable=s_zip_raw_var).pack(anchor="w", padx=6, pady=3)

t3.columnconfigure(1, weight=1)

# Hàm tự động lưu mỗi khi có thay đổi
_init_done = False

def auto_save_settings(*args):
    if not _init_done:
        return
    try:
        t_str = s_threads_var.get().strip()
        threads = int(t_str) if t_str else 20
        if threads < 1: threads = 20
    except ValueError:
        threads = 20

    cfg = C.load()
    cfg["folder_id"]        = s_folder_var.get().strip()
    cfg["credentials_file"] = s_cred_var.get().strip()
    cfg["vsf_path"]         = s_vsf_var.get().strip()
    cfg["threads"]          = threads
    cfg["delete_raw_texts"] = s_del_raw_var.get()
    cfg["delete_texts"]     = s_del_txt_var.get()
    cfg["nen_raw_texts"]    = s_zip_raw_var.get()
    C.save(cfg)

# Đăng ký các trace để tự lưu
s_folder_var.trace_add("write", auto_save_settings)
s_cred_var.trace_add("write", auto_save_settings)
s_vsf_var.trace_add("write", auto_save_settings)
s_threads_var.trace_add("write", auto_save_settings)
s_del_raw_var.trace_add("write", auto_save_settings)
s_del_txt_var.trace_add("write", auto_save_settings)
s_zip_raw_var.trace_add("write", auto_save_settings)

def open_settings_file():
    """Mở settings.json bằng trình soạn thảo mặc định của OS."""
    import subprocess
    path = os.path.abspath(C.CONFIG_FILE)
    if not os.path.exists(path):
        C.save(C.load())  # tạo file nếu chưa có
    try:
        os.startfile(path)           # Windows
    except AttributeError:
        subprocess.run(["xdg-open", path])  # Linux fallback

def reset_token():
    tok = C.token_file()
    if os.path.exists(tok):
        os.remove(tok)
        log(f"🗑 Đã xoá {os.path.basename(tok)} — sẽ yêu cầu xác thực lại lần sau.")
        messagebox.showinfo("Done", f"Đã xoá {os.path.basename(tok)}")
    else:
        messagebox.showinfo("Thông báo", f"Không tìm thấy file token tại:\n{tok}")

sf = ttk.Frame(t3); sf.grid(row=12, column=0, columnspan=3, pady=12, padx=6, sticky="w")
ttk.Button(sf, text="📂 Mở settings.json",   command=open_settings_file).pack(side="left", padx=4)
ttk.Button(sf, text="🔑 Reset token", command=reset_token).pack(side="left", padx=4)

# Dòng chữ giải thích nhỏ và mờ dưới nút Reset Token
lbl_reset_brief = ttk.Label(t3, text="* Nhấn Reset token sẽ yêu cầu đăng nhập lại tài khoản Google ở lần chạy OCR tiếp theo.",
                            foreground="#888888", font=("Helvetica", 8))
lbl_reset_brief.grid(row=13, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 10))

_init_done = True

# ─ Status + progress (dùng chung cả 3 tab) ───────────────────────────────────
bot = ttk.Frame(root); bot.pack(fill="x", padx=8, pady=(2, 2))
status = ttk.Label(bot, text="Sẵn sàng."); status.pack(anchor="w")
bar = ttk.Progressbar(bot, maximum=100); bar.pack(fill="x", pady=2)

log_box = scrolledtext.ScrolledText(root, state="disabled", height=10, font=("Consolas", 9))
log_box.pack(fill="both", expand=True, padx=8, pady=(0,6))

def _on_exit():
    if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
        if C.state.observer:
            try: C.state.observer.stop()
            except Exception: pass
        root.destroy()

root.protocol("WM_DELETE_WINDOW", _on_exit)

if __name__ == "__main__":
    root.mainloop()

