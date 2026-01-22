
# -*- coding: utf-8 -*-
# app_py_live_2ndver.py
# EN-only UI, emissivity dropdown moved to top beside "Connection" (two columns),
# linear calibration m/a (NTC 10K), confirm dialog before Snapshot/Record,
# snapshot saves PNG+CSV+JSON(+NPY), live viewer (Matplotlib in PySide6), ROI & Min/Max overlay.

import sys, os, time, threading, queue, json
import numpy as np
import serial, serial.tools.list_ports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout,
    QLabel, QComboBox, QHBoxLayout, QGroupBox, QWidget
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPalette, QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

# === Import class hasil konversi .ui ===
from ui_main import Ui_MainWindow  # pyside6-uic main.ui -o ui_main.py

# ==== Optional: OpenCV untuk video ====
try:
    import cv2
    HAVE_CV2 = True
except Exception:
    HAVE_CV2 = False

# ==== Konfigurasi serial (samakan dengan firmware) ====
BAUD = 921600
TIMEOUT = 0.3
running = True
frame_q = queue.Queue(maxsize=3)

# ==== Kalibrasi linear (NTC 10K): T_cal = m*T_raw + a ====
CALIB_M = 1.23648  # slope m
CALIB_A = -5.50616 # intercept a
USE_CALIBRATION = True

def apply_calibration(frame: np.ndarray) -> np.ndarray:
    """Gunakan inverse: Temp = (MLX - a) / m"""
    return ((frame - CALIB_A) / CALIB_M) if USE_CALIBRATION else frame

def compute_clim(frame: np.ndarray, mode: str, p_lo=5, p_hi=95):
    flat = frame[np.isfinite(frame) & (frame != 0)]
    if flat.size == 0:
        return (0.0, 1.0)
    if mode.lower().startswith("percent"):
        vmin = float(np.percentile(flat, p_lo))
        vmax = float(np.percentile(flat, p_hi))
    else:
        vmin = float(np.min(flat)); vmax = float(np.max(flat))
    if abs(vmax - vmin) < 1e-6:
        vmax = vmin + 1.0
    return (vmin, vmax)

def serial_worker(get_port_callable):
    """Reads frames from serial as 'FRAME_START' + CSV(768) + 'FRAME_END' (24x32)."""
    global running
    ser = None

    def open_serial():
        nonlocal ser
        while running:
            try:
                port = get_port_callable()
                if not port:
                    time.sleep(0.3)
                    continue
                ser = serial.Serial(port, BAUD, timeout=TIMEOUT)
                print(f"[Serial] Connected {port} @ {BAUD}")
                return True
            except Exception as e:
                print(f"[Serial] Open fail: {e}")
                time.sleep(0.5)
                continue
        return False

    if not open_serial():
        return

    last_ts = time.time()
    while running:
        try:
            line = ser.readline().decode(errors="ignore").strip()
        except Exception as e:
            print(f"[Serial] Read error: {e} -> reconnect")
            try:
                ser.close()
            except:
                pass
            if not open_serial():
                break
            continue

        if not line:
            continue

        if line == "FRAME_START":
            try:
                data_line = ser.readline().decode(errors="ignore").strip()
                end_line = ser.readline().decode(errors="ignore").strip()
                if end_line != "FRAME_END":
                    print("[Serial] Invalid frame"); continue
                values = data_line.split(",")
                if len(values) != 768:
                    print(f"[Serial] CSV len {len(values)} != 768"); continue
                frame = np.array(values, dtype=float).reshape((24, 32))
            except Exception:
                print("[Serial] Parse error")
                continue

            frame = apply_calibration(frame)

            try:
                if frame_q.full():
                    _ = frame_q.get_nowait()
                frame_q.put_nowait(frame)
            except queue.Full:
                pass

            now = time.time()
            dt = now - last_ts
            last_ts = now
            fps = (1.0 / dt) if dt > 0 else 0.0
            print(f"[Serial] ✅ {fps:.1f} fps")

    try:
        ser.close()
    except:
        pass
    print("[Serial] Thread stop")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Setup UI ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # === Theme: accent blue, soft cards, modern font ===
        accent = "#1976d2"  # blue 700
        accent_dark = "#0d47a1"
        bg = "#ffffff"
        border = "#d0d7de"  # soft grey
        text = "#111827"    # near-black
        font_family = "Segoe UI, Roboto, Arial"

        self.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background: {bg}; color: {text}; font-family: {font_family};
        }}
        QGroupBox {{
            border: 1px solid {border}; border-radius: 6px; margin-top: 8px; padding: 8px;
            font-weight: 600;
        }}
        QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 4px; }}
        QFrame#plotContainer {{ border: 1px solid {border}; border-radius: 8px; background: #fafafa; }}
        QPushButton {{
            background: #f5f7ff; color: {accent}; border: 1px solid {accent}; border-radius: 6px; padding: 6px 10px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background: #eaf1ff; }}
        QPushButton:pressed {{ background: #dbe8ff; }}
        QPushButton:disabled {{ color: #8fa7c7; border-color: #8fa7c7; background: #f0f3f8; }}
        QPushButton#btnStart, QPushButton#btnStop, QPushButton#btnRecord {{
            background: {accent}; color: white; border: 1px solid {accent_dark};
        }}
        QPushButton#btnStart:hover, QPushButton#btnStop:hover, QPushButton#btnRecord:hover {{ background: {accent_dark}; }}
        QComboBox {{ background: #ffffff; color: {text}; border: 1px solid {border}; border-radius: 6px; padding: 4px 8px; }}
        QComboBox QAbstractItemView {{ background: #ffffff; color: {text}; selection-background-color: #eaf1ff; selection-color: {text}; border: 1px solid {border}; }}
        QCheckBox {{ background: transparent; color: {text}; font-weight: 600; }}
        QLabel#lblTminVal, QLabel#lblTmaxVal, QLabel#lblTavgVal,
        QLabel#lblTminROI, QLabel#lblTmaxROI, QLabel#lblTavgROI {{
            background: #ffffff; color: {text}; border: 1px solid {border}; border-radius: 6px; padding: 4px 8px; font-weight: 600;
        }}
        QStatusBar {{ background: #f8fafc; color: {text}; }}
        """)

        # Palette & base font size
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(bg))
        pal.setColor(QPalette.ColorRole.Base, QColor(bg))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(text))
        pal.setColor(QPalette.ColorRole.Text, QColor(text))
        self.setPalette(pal)
        base_font = QFont("Segoe UI", 10)
        self.setFont(base_font)

        # --- Plot canvas ---
        self.fig, self.ax = plt.subplots(figsize=(7.2, 5.2), dpi=100)
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        self.canvas = FigureCanvas(self.fig)

        # Ensure plotContainer has a layout
        if self.ui.centralwidget.findChild(QVBoxLayout, "verticalLayout_plot") is None:
            self.ui.plotContainer.setLayout(QVBoxLayout())
        self.ui.plotContainer.layout().addWidget(self.canvas)

        self.im = self.ax.imshow(np.zeros((24, 32)), cmap="inferno", vmin=20, vmax=30, interpolation="nearest")
        # Colorbar
        self.cbar = self.fig.colorbar(self.im, ax=self.ax)
        label_text = "Temperature (°C, calibrated)" if USE_CALIBRATION else "Temperature (°C)"
        self.cbar.ax.set_ylabel(label_text, labelpad=10, fontsize=11, fontweight='bold', color='#111827')
        self.cbar.ax.tick_params(color='#111827', labelcolor='#111827', labelsize=10)

        # Axes aesthetics
        self.ax.set_title("Thermal Heatmap — GUI fps", fontsize=14, fontweight='bold', color='#111827')
        self.ax.set_xlabel("X Pixel", fontsize=12)
        self.ax.set_ylabel("Y Pixel", fontsize=12)
        self.ax.tick_params(colors='#111827', which='both', labelsize=10)
        for spine in self.ax.spines.values():
            spine.set_color('#e5e7eb')
        self.fig.subplots_adjust(left=0.08, right=0.88, top=0.92, bottom=0.10)

        # --- Overlay min/max ---
        self.min_marker = None
        self.max_marker = None
        self.min_text = None
        self.max_text = None

        # --- Signals ---
        self.ui.btnStart.clicked.connect(self.on_start)
        self.ui.btnStop.clicked.connect(self.on_stop)
        self.ui.btnCapture.clicked.connect(self.on_capture)
        self.ui.btnRecord.clicked.connect(self.on_record_toggle)
        self.ui.btnRefreshPorts.clicked.connect(self.refresh_ports)
        self.ui.chkCalibrated.toggled.connect(self.on_toggle_calib)
        self.ui.comboAutoScale.currentTextChanged.connect(self.on_change_autoscale)
        self.ui.comboPort.currentIndexChanged.connect(self.on_port_change)

        # --- Emissivity dropdown beside "Connection" ---
        conn_group = self._find_groupbox_of(self.ui.comboPort)
        if conn_group and conn_group.parentWidget() and conn_group.parentWidget().layout():
            main_layout = conn_group.parentWidget().layout()
            idx = None
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                w = item.widget() if item is not None else None
                if w is conn_group:
                    idx = i
                    break

            mat_group = QGroupBox("Material")
            mat_group.setObjectName("groupMaterial")
            mat_layout = QHBoxLayout(mat_group)
            mat_layout.setContentsMargins(8, 8, 8, 8)
            mat_layout.setSpacing(8)

            self.lblEmis = QLabel("Material (emissivity):")
            self.comboEmis = QComboBox()
            emis_list = ["e = 0.950", "e = 0.918", "e = 0.092", "e = 0.88", "e = 0.05"]
            self.comboEmis.addItems(emis_list)
            idx_default = emis_list.index("e = 0.05")
            self.comboEmis.setCurrentIndex(idx_default)

            mat_layout.addWidget(self.lblEmis)
            mat_layout.addWidget(self.comboEmis, 1)

            hrow = QHBoxLayout()
            hrow.setContentsMargins(0, 0, 0, 0)
            hrow.setSpacing(12)
            if idx is not None:
                main_layout.removeWidget(conn_group)
                hrow.addWidget(conn_group, stretch=1)
                hrow.addWidget(mat_group, stretch=1)
                main_layout.insertLayout(idx, hrow)
            else:
                hrow.addWidget(conn_group, stretch=1)
                hrow.addWidget(mat_group, stretch=1)
                main_layout.insertLayout(0, hrow)

        # --- Init ---
        self.latest_frame = np.zeros((24, 32), dtype=float)
        self.auto_scale_mode = "Min - Max"
        self.refresh_ports(select_default="COM3")

        self.recording = False
        self.record_dir = None
        self.record_idx = 0
        self.video_writer = None
        self.video_fps = 4
        self.video_path = None
        self.video_size = None
        # --- Added: to keep start time & metadata path for record session ---
        self.record_start_ts = None
        self.record_info_path = None

        # Timer ~60 Hz
        self.gui_timer_id = self.startTimer(16)
        self.gui_frames = 0
        self.gui_last_ts = time.time()

        self.connect_hover()
        self.enable_roi()
        self.statusBar().showMessage("Ready. Select COM port, then Start.")

    # ---------- Utilities for layout & data ----------
    def _find_groupbox_of(self, child_widget: QWidget) -> QGroupBox | None:
        """Ascend parents to find the QGroupBox containing the given child widget."""
        p = child_widget.parentWidget()
        while p is not None and not isinstance(p, QGroupBox):
            p = p.parentWidget()
        return p if isinstance(p, QGroupBox) else None

    def get_emissivity_value(self) -> float:
        text = self.comboEmis.currentText()
        try:
            return float(text.split("=")[1].strip())
        except Exception:
            return 0.05

    def on_port_change(self):
        self.port_device = self.ui.comboPort.currentData()

    def refresh_ports(self, select_default=None):
        self.ui.comboPort.clear()
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            self.ui.comboPort.addItem(f"{p.device} — {p.description}", userData=p.device)
        if select_default:
            for i in range(self.ui.comboPort.count()):
                if self.ui.comboPort.itemData(i) == select_default:
                    self.ui.comboPort.setCurrentIndex(i)
                    break
        if self.ui.comboPort.count() == 0:
            QMessageBox.warning(self, "COM Ports", "No ports detected.")

    # ---------- Added: Helpers for naming ----------
    def _safe_slug(self, text: str) -> str:
        """
        Ubah teks jadi slug aman untuk nama file:
        - huruf kecil
        - spasi => '-'
        - buang karakter non-alfanumerik kecuali '-', '_', '.', '='
        """
        import re
        t = text.strip().lower()
        t = t.replace(' ', '-')
        t = re.sub(r'[^a-z0-9\-\_\.\=]', '', t)
        t = re.sub(r'-{2,}', '-', t).strip('-')
        return t

    def _current_material_slug(self) -> str:
        """
        Bangun slug dari label emissivity, contoh:
        'e = 0.950' -> 'e=0.950'
        'aluminium (e=0.05)' -> 'aluminium-e=0.05'
        """
        label = self.comboEmis.currentText() or ""
        label = label.replace(" ", "")
        return self._safe_slug(label)

    def _timestamp(self) -> str:
        return time.strftime("%Y%m%d-%H%M%S")

    # ---------- Start/Stop ----------
    def on_start(self):
        global running
        if self.ui.comboPort.count() == 0:
            QMessageBox.warning(self, "Serial", "Please select a COM port first.")
            return
        running = True
        if not hasattr(self, "th") or not self.th.is_alive():
            self.th = threading.Thread(target=serial_worker, args=(lambda: self.ui.comboPort.currentData(),), daemon=True)
            self.th.start()
        self.statusBar().showMessage(f"Streaming from {self.ui.comboPort.currentData()} @ {BAUD}")
        QTimer.singleShot(2000, self._check_no_data)

    def _check_no_data(self):
        if np.all(self.latest_frame == 0):
            QMessageBox.information(
                self, "No data yet",
                "No frame received yet.\n\nCheck:\n• Correct COM port\n• Baud 921600 matches firmware\n• Firmware sends 'FRAME_START/END' + 768 values"
            )

    def on_stop(self):
        global running
        running = False
        self.statusBar().showMessage("Stopped.")

    # ---------- Capture / Record ----------
    def _confirm_material(self) -> bool:
        r = QMessageBox.question(
            self,
            "Confirm Material",
            "Is the material selection correct?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        return r == QMessageBox.StandardButton.Yes

    def on_capture(self):
        # Ask confirmation first
        if not self._confirm_material():
            self.statusBar().showMessage("Snapshot cancelled. Adjust emissivity if needed.")
            return

        # Prepare paths (Modified naming)
        mat_slug = self._current_material_slug()
        ts = self._timestamp()
        out_dir = os.path.join(os.getcwd(), "snapshots")
        os.makedirs(out_dir, exist_ok=True)

        base = f"snapshot_{mat_slug}_{ts}"
        png_path  = os.path.join(out_dir, f"{base}.png")
        csv_path  = os.path.join(out_dir, f"{base}.csv")
        json_path = os.path.join(out_dir, f"{base}.json")
        npy_path  = os.path.join(out_dir, f"{base}.npy")  # optional, keep for compatibility

        # Save figure (PNG)
        self.fig.canvas.draw()
        self.fig.savefig(png_path, dpi=150)

        # Save CSV (current calibrated frame)
        frame_to_save = np.array(self.latest_frame, dtype=float)
        np.savetxt(csv_path, frame_to_save, delimiter=",", fmt="%.3f")

        # Save NPY (optional)
        try:
            np.save(npy_path, frame_to_save)
        except Exception:
            pass

        # Save metadata JSON
        meta = {
            "timestamp": ts,
            "shape": {"rows": 24, "cols": 32},
            "calibration": {
                "enabled": bool(USE_CALIBRATION),
                "slope_m": CALIB_M,
                "intercept_a": CALIB_A,
                "formula": "T_cal = m*T_raw + a"
            },
            "emissivity": {
                "label": self.comboEmis.currentText(),
                "value": self.get_emissivity_value()
            },
            "auto_scale_mode": self.auto_scale_mode,
            "serial": {
                "port": self.ui.comboPort.currentData(),
                "baud": BAUD
            },
            "stats": {
                "min_C": float(np.nanmin(frame_to_save)),
                "max_C": float(np.nanmax(frame_to_save)),
                "mean_C": float(np.nanmean(frame_to_save))
            },
            "outputs": {
                "png": os.path.basename(png_path),
                "csv": os.path.basename(csv_path),
                "json": os.path.basename(json_path),
                "npy": os.path.basename(npy_path)
            }
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        QMessageBox.information(self, "Saved", f"Saved:\n{png_path}\n{csv_path}\n{json_path}")

    # --- Video writer (AVI, MJPG->XVID) ---
    def _init_video_writer(self):
        if not HAVE_CV2:
            return None, None

        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        w, h = int(getattr(renderer, 'width', 0)), int(getattr(renderer, 'height', 0))
        if w <= 0 or h <= 0:
            w, h = map(int, self.fig.canvas.get_width_height())
        if w <= 0 or h <= 0:
            return None, None

        # Modified naming for AVI
        mat_slug = self._current_material_slug()
        start_ts = self.record_start_ts or self._timestamp()
        avi_path = os.path.join(self.record_dir, f"record_{mat_slug}_{start_ts}.avi")

        for fourcc_name in ('MJPG', 'XVID'):
            fourcc = cv2.VideoWriter_fourcc(*fourcc_name)
            writer = cv2.VideoWriter(avi_path, fourcc, float(self.video_fps), (w, h), True)
            if writer is not None and writer.isOpened():
                print(f"[Video] Writer opened: {avi_path}, codec={fourcc_name}, size=({w},{h}), fps={self.video_fps}")
                return writer, avi_path
            else:
                try:
                    if writer is not None:
                        writer.release()
                except:
                    pass
        return None, None

    def on_record_toggle(self):
        # If starting to record, confirm material first
        if not self.recording:
            if not self._confirm_material():
                self.statusBar().showMessage("Recording cancelled. Adjust emissivity if needed.")
                return

            mat_slug = self._current_material_slug()
            ts = self._timestamp()
            self.record_start_ts = ts

            # Modified: folder name includes material & timestamp
            self.record_dir = os.path.join(os.getcwd(), f"record_{mat_slug}_{ts}")
            os.makedirs(self.record_dir, exist_ok=True)

            self.video_writer = None
            self.video_path = None
            self.video_size = None

            if HAVE_CV2:
                writer, path = self._init_video_writer()
                if writer is None:
                    QMessageBox.warning(self, "Video Writer", "Failed to open VideoWriter (MJPG/XVID). Recording will be PNG+NPY per frame.")
                else:
                    self.video_writer = writer
                    self.video_path = path
                    self.fig.canvas.draw()
                    renderer = self.fig.canvas.get_renderer()
                    w, h = int(getattr(renderer, 'width', 0)), int(getattr(renderer, 'height', 0))
                    if w <= 0 or h <= 0:
                        w, h = map(int, self.fig.canvas.get_width_height())
                    self.video_size = (w, h)
            else:
                QMessageBox.information(self, "Video Writer", "OpenCV not installed.\nInstall: pip install opencv-python\nRecording will be PNG+NPY per frame.")

            # Write metadata at start (Modified naming)
            meta = {
                "start_time": ts,
                "port": self.ui.comboPort.currentData(),
                "baud": BAUD,
                "use_calibration": USE_CALIBRATION,
                "calibration": {"slope_m": CALIB_M, "intercept_a": CALIB_A, "formula": "T_cal = m*T_raw + a"},
                "auto_scale_mode": self.auto_scale_mode,
                "fps": self.video_fps,
                "video_path": self.video_path,
                "emissivity": {
                    "label": self.comboEmis.currentText(),
                    "value": self.get_emissivity_value()
                }
            }
            info_name = f"record_info_{mat_slug}_{ts}.json"
            self.record_info_path = os.path.join(self.record_dir, info_name)
            with open(self.record_info_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

            self.record_idx = 0
            self.recording = True
            self.ui.btnRecord.setText("⏹ Stop Record")
            self.statusBar().showMessage(f"Recording → {self.record_dir}")

        else:
            # Stop recording
            self.recording = False
            if self.video_writer is not None:
                try:
                    self.video_writer.release()
                except:
                    pass
            self.video_writer = None
            self.ui.btnRecord.setText("⏺ Record")

            end_ts = self._timestamp()
            info_path = self.record_info_path or os.path.join(self.record_dir, "record_info.json")
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}
            meta["end_time"] = end_ts
            meta["frames"] = self.record_idx
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

            self.statusBar().showMessage(f"Recording finished → {self.record_dir}")

    # ---------- Calibration toggle & autoscale ----------
    def on_toggle_calib(self, checked: bool):
        global USE_CALIBRATION
        USE_CALIBRATION = checked
        label_text = "Temperature (°C, calibrated)" if checked else "Temperature (°C)"
        self.cbar.ax.set_ylabel(label_text, labelpad=10, fontsize=11, fontweight='bold', color='#111827')
        self.fig.canvas.draw_idle()
        self.statusBar().showMessage(f"Calibration: {'ON' if checked else 'OFF'}")

    def on_change_autoscale(self, text: str):
        self.auto_scale_mode = text or "Min - Max"

    # ---------- Hover ----------
    def connect_hover(self):
        def on_move(event):
            if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
                return
            col = int(round(event.xdata))
            row = int(round(event.ydata))
            if 0 <= col < 32 and 0 <= row < 24:
                T = self.latest_frame[row, col]
                self.statusBar().showMessage(f"Pixel r={row}, c={col} → {T:.2f} °C")
        self.fig.canvas.mpl_connect('motion_notify_event', on_move)

    # ---------- ROI ----------
    def enable_roi(self):
        def on_select(eclick, erelease):
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            if None in (x1, y1, x2, y2):
                return
            cmin, cmax = sorted([int(np.floor(x1)), int(np.floor(x2))])
            rmin, rmax = sorted([int(np.floor(y1)), int(np.floor(y2))])
            cmin = max(0, min(31, cmin)); cmax = max(0, min(31, cmax))
            rmin = max(0, min(23, rmin)); rmax = max(0, min(23, rmax))
            roi = self.latest_frame[rmin:rmax+1, cmin:cmax+1]
            flat = roi[(roi != 0) & np.isfinite(roi)]
            if flat.size:
                if self.ui.lblTminROI: self.ui.lblTminROI.setText(f"{np.min(flat):.2f} °C")
                if self.ui.lblTmaxROI: self.ui.lblTmaxROI.setText(f"{np.max(flat):.2f} °C")
                if self.ui.lblTavgROI: self.ui.lblTavgROI.setText(f"{np.mean(flat):.2f} °C")
            self.statusBar().showMessage(
                f"ROI r[{rmin}:{rmax}] c[{cmin}:{cmax}] — "
                f"min {np.min(flat):.2f}°C, max {np.max(flat):.2f}°C, avg {np.mean(flat):.2f}°C"
                if flat.size else
                f"ROI r[{rmin}:{rmax}] c[{cmin}:{cmax}]"
            )
        self.roi_selector = RectangleSelector(self.ax, on_select, useblit=True, interactive=True, button=[1], spancoords='data', minspanx=1, minspany=1)

    # ---------- Min/Max overlay ----------
    def _update_minmax_overlay(self, frame: np.ndarray):
        mask = np.isfinite(frame) & (frame != 0)
        if not mask.any():
            if self.min_marker: self.min_marker.set_visible(False)
            if self.max_marker: self.max_marker.set_visible(False)
            if self.min_text: self.min_text.set_visible(False)
            if self.max_text: self.max_text.set_visible(False)
            return

        minval = frame[mask].min()
        maxval = frame[mask].max()
        rmin, cmin = np.argwhere(frame == minval)[0]
        rmax, cmax = np.argwhere(frame == maxval)[0]

        if self.min_marker is None:
            self.min_marker = self.ax.scatter([cmin], [rmin], s=80, facecolors='cyan', edgecolors='black', zorder=3, label='Min')
            self.min_text = self.ax.text(cmin+0.5, rmin-0.5, f"Min {minval:.2f}°C", color='#111827', fontsize=10, zorder=4,
                                         bbox=dict(facecolor='white', edgecolor='#d0d7de', boxstyle='round,pad=0.2'))
        else:
            self.min_marker.set_offsets([[cmin, rmin]])
            self.min_marker.set_visible(True)
            self.min_text.set_text(f"Min {minval:.2f}°C")
            self.min_text.set_position((cmin+0.5, rmin-0.5))
            self.min_text.set_visible(True)

        if self.max_marker is None:
            self.max_marker = self.ax.scatter([cmax], [rmax], s=80, facecolors='yellow', edgecolors='black', zorder=3, label='Max')
            self.max_text = self.ax.text(cmax+0.5, rmax-0.5, f"Max {maxval:.2f}°C", color='#111827', fontsize=10, zorder=4,
                                         bbox=dict(facecolor='white', edgecolor='#d0d7de', boxstyle='round,pad=0.2'))
        else:
            self.max_marker.set_offsets([[cmax, rmax]])
            self.max_marker.set_visible(True)
            self.max_text.set_text(f"Max {maxval:.2f}°C")
            self.max_text.set_position((cmax+0.5, rmax-0.5))
            self.max_text.set_visible(True)

    # ---------- Timer ----------
    def timerEvent(self, event):
        try:
            frame = frame_q.get_nowait()
        except queue.Empty:
            return

        self.latest_frame = frame
        mode = self.auto_scale_mode
        vmin, vmax = compute_clim(frame, mode=("percentile" if mode.lower().startswith("percent") else "minmax"))
        self.im.set_data(frame)
        self.im.set_clim(vmin=vmin, vmax=vmax)
        self._update_minmax_overlay(frame)
        self.fig.canvas.draw()

        flat = frame[(frame != 0) & np.isfinite(frame)]
        if flat.size:
            if self.ui.lblTminVal: self.ui.lblTminVal.setText(f"{np.min(flat):.2f} °C")
            if self.ui.lblTmaxVal: self.ui.lblTmaxVal.setText(f"{np.max(flat):.2f} °C")
            if self.ui.lblTavgVal: self.ui.lblTavgVal.setText(f"{np.mean(flat):.2f} °C")

        if self.recording and self.record_dir:
            self.record_idx += 1
            if self.video_writer is not None and HAVE_CV2:
                renderer = self.fig.canvas.get_renderer()
                w_cur, h_cur = int(getattr(renderer, 'width', 0)), int(getattr(renderer, 'height', 0))
                if w_cur <= 0 or h_cur <= 0:
                    w_cur, h_cur = map(int, self.fig.canvas.get_width_height())
                buf = np.frombuffer(self.fig.canvas.buffer_rgba(), dtype=np.uint8)
                expected = w_cur * h_cur * 4
                if buf.size >= expected:
                    img = buf[:expected].reshape((h_cur, w_cur, 4))
                    bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    if self.video_size and (w_cur, h_cur) != self.video_size:
                        bgr = cv2.resize(bgr, self.video_size, interpolation=cv2.INTER_AREA)
                    self.video_writer.write(bgr)
            else:
                # Modified naming for per-frame files
                mat_slug = self._current_material_slug()
                frame_ts = self._timestamp()  # waktu aktual saat frame disimpan
                base = f"frame_{mat_slug}_{frame_ts}_{self.record_idx:04d}"
                png_path = os.path.join(self.record_dir, f"{base}.png")
                npy_path = os.path.join(self.record_dir, f"{base}.npy")
                self.fig.savefig(png_path, dpi=120)
                np.save(npy_path, frame)

        # Update GUI title with FPS (GUI side)
        self.gui_frames += 1
        now = time.time()
        if now - self.gui_last_ts >= 1.0:
            self.ax.set_title(f"Thermal Heatmap — GUI {self.gui_frames:.0f} fps", fontsize=14, fontweight='bold', color='#111827')
            self.gui_frames = 0
            self.gui_last_ts = now


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()