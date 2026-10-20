import os
import datetime
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QFrame, QProgressBar, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QAction, QColor

from archive_engine import ArchiveItem


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


class ArchiveView(QWidget):
    item_double_clicked = Signal(str, bool)   # (internal_path, is_dir)
    extract_selected = Signal(list)           # [internal_paths]
    selection_changed = Signal(int, int)      # (selected_count, selected_bytes)
    image_preview_requested = Signal(str)     # (internal_path) - 실시간 이미지 미리보기 신호

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_items: List[ArchiveItem] = []
        self.current_prefix = ""
        self.history = []
        self.filter_keyword = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Efficiency Dashboard Banner
        self.stats_banner = QFrame()
        self.stats_banner.setObjectName("StatsBanner")
        stats_layout = QHBoxLayout(self.stats_banner)
        stats_layout.setContentsMargins(14, 6, 14, 6)
        stats_layout.setSpacing(12)

        self.stats_summary_lbl = QLabel("열린 아카이브 없음 (Ctrl+O로 열기)")
        self.stats_summary_lbl.setObjectName("StatsTitle")
        stats_layout.addWidget(self.stats_summary_lbl)

        self.efficiency_bar = QProgressBar()
        self.efficiency_bar.setFixedSize(140, 16)
        self.efficiency_bar.setRange(0, 100)
        self.efficiency_bar.setValue(0)
        self.efficiency_bar.setTextVisible(False)
        self.efficiency_bar.setToolTip("압축으로 절약된 용량 비율")
        stats_layout.addWidget(self.efficiency_bar)

        self.stats_pill = QLabel("0% 절약")
        self.stats_pill.setObjectName("StatsPill")
        stats_layout.addWidget(self.stats_pill)

        stats_layout.addStretch()

        # Instant Live Search Filter Box
        self.search_box = QLineEdit()
        self.search_box.setObjectName("SearchBox")
        self.search_box.setPlaceholderText("🔍 파일명 즉시 검색...")
        self.search_box.textChanged.connect(self._on_search_changed)
        stats_layout.addWidget(self.search_box)

        layout.addWidget(self.stats_banner)

        # 2. Navigation Bar
        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("NavFrame")
        nav_layout = QHBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(14, 6, 14, 6)
        nav_layout.setSpacing(8)

        self.back_btn = QPushButton("◀ 뒤로")
        self.back_btn.setFixedWidth(80)
        self.back_btn.clicked.connect(self._go_back)

        self.up_btn = QPushButton("▲ 상위 폴더")
        self.up_btn.setFixedWidth(116)
        self.up_btn.clicked.connect(self._go_up)

        self.path_edit = QLineEdit()
        self.path_edit.setObjectName("PathEdit")
        self.path_edit.setReadOnly(True)
        self.path_edit.setText("/")

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.up_btn)
        nav_layout.addWidget(self.path_edit)
        layout.addWidget(self.nav_frame)

        # 3. Main Splitter: Table (Left) + High-Speed Image Preview Panel (Right)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        # File Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "이름", "압축 크기", "원본 크기", "압축률", "종류", "수정한 날짜", "보안", "CRC-32"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 8):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        self.main_splitter.addWidget(self.table)

        # Right: Modern Image Preview Panel (기본 활성화)
        self.preview_panel = QFrame()
        self.preview_panel.setObjectName("PreviewPanel")
        self.preview_panel.setFixedWidth(290)
        prev_layout = QVBoxLayout(self.preview_panel)
        prev_layout.setContentsMargins(14, 12, 14, 14)
        prev_layout.setSpacing(10)

        prev_header = QHBoxLayout()
        self.prev_title = QLabel("🖼️ 이미지 미리보기")
        self.close_prev_btn = QPushButton("✕")
        self.close_prev_btn.setFixedSize(22, 22)
        self.close_prev_btn.setCursor(Qt.PointingHandCursor)
        self.close_prev_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-weight: 700;
                color: #94A3B8;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #EF4444;
            }
        """)
        self.close_prev_btn.clicked.connect(lambda: self.set_preview_visible(False))
        prev_header.addWidget(self.prev_title)
        prev_header.addStretch()
        prev_header.addWidget(self.close_prev_btn)
        prev_layout.addLayout(prev_header)

        # Image Container
        self.img_container = QFrame()
        img_box_layout = QVBoxLayout(self.img_container)
        img_box_layout.setContentsMargins(6, 6, 6, 6)

        self.preview_img_lbl = QLabel("목록에서 이미지를\n클릭하면 즉시 표시됩니다.")
        self.preview_img_lbl.setAlignment(Qt.AlignCenter)
        self.preview_img_lbl.setWordWrap(True)
        img_box_layout.addWidget(self.preview_img_lbl)
        prev_layout.addWidget(self.img_container, 1)

        # Image Info Details
        self.img_info_lbl = QLabel("")
        self.img_info_lbl.setWordWrap(True)
        prev_layout.addWidget(self.img_info_lbl)

        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 0)

        layout.addWidget(self.main_splitter, 1)

        from theme import get_theme_dict
        self.apply_theme(get_theme_dict("Aura Indigo"))

    def apply_theme(self, theme: dict):
        self.preview_panel.setStyleSheet(f"""
            QFrame#PreviewPanel {{
                background-color: {theme['bg_card']};
                border-left: 1.5px solid {theme['border_color']};
            }}
        """)
        self.prev_title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {theme['text_main']};
            border: none;
            background: transparent;
        """)
        self.img_container.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['bg_window']};
                border: 1.5px dashed {theme['border_color']};
                border-radius: 8px;
            }}
        """)
        self.preview_img_lbl.setStyleSheet(f"""
            color: {theme['text_muted']};
            font-size: 12px;
            border: none;
            background: transparent;
        """)
        self.img_info_lbl.setStyleSheet(f"""
            color: {theme['text_secondary']};
            font-size: 11px;
            line-height: 1.5;
            border: none;
            background: transparent;
        """)

    def set_preview_visible(self, visible: bool):
        self.preview_panel.setVisible(visible)

    def toggle_preview_panel(self):
        self.preview_panel.setVisible(not self.preview_panel.isVisible())

    def clear_image_preview(self, msg: str = "목록에서 이미지를\n클릭하면 즉시 표시됩니다."):
        self.preview_img_lbl.clear()
        self.preview_img_lbl.setWordWrap(True)
        self.preview_img_lbl.setText(msg)
        self.img_info_lbl.setText("")

    def update_image_preview(self, img_bytes: bytes, filename: str, filesize: int):
        if not img_bytes:
            self.clear_image_preview("미리보기를 불러올 수 없습니다.")
            return

        pixmap = QPixmap()
        if pixmap.loadFromData(img_bytes):
            w = pixmap.width()
            h = pixmap.height()
            box_w = max(220, self.img_container.width() - 16)
            box_h = max(220, self.img_container.height() - 16)
            scaled = pixmap.scaled(box_w, box_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.preview_img_lbl.setWordWrap(False)
            self.preview_img_lbl.setPixmap(scaled)
            self.img_info_lbl.setText(
                f"<b>파일명:</b> {os.path.basename(filename)}<br>"
                f"<b>해상도:</b> {w} × {h} px<br>"
                f"<b>크기:</b> {format_bytes(filesize)}"
            )
            self.preview_panel.show()
            total_w = self.main_splitter.width()
            if total_w > 400 and (len(self.main_splitter.sizes()) < 2 or self.main_splitter.sizes()[1] < 100):
                self.main_splitter.setSizes([total_w - 290, 290])
        else:
            self.clear_image_preview("지원되지 않는 이미지 포맷입니다.")
            self.img_info_lbl.setText(f"<b>파일명:</b> {os.path.basename(filename)}")

    def set_items(self, items: List[ArchiveItem]):
        self.clear_image_preview()
        self.all_items = items
        self.current_prefix = ""
        self.history.clear()
        self.filter_keyword = ""
        self.search_box.clear()
        self._update_stats_banner()
        self._refresh_view()

    def _update_stats_banner(self):
        file_items = [it for it in self.all_items if not it.is_dir]
        if not file_items:
            self.stats_summary_lbl.setText("열린 아카이브 없음 (Ctrl+O로 열기)")
            self.efficiency_bar.setValue(0)
            self.stats_pill.setText("0% 절약")
            return

        total_orig = sum(it.original_size for it in file_items)
        total_comp = sum(it.compressed_size for it in file_items)
        ratio = (1.0 - (total_comp / total_orig)) * 100.0 if total_orig > 0 else 0.0

        self.stats_summary_lbl.setText(
            f"파일 {len(file_items)}개  |  원본 {format_bytes(total_orig)} -> 압축 {format_bytes(total_comp)}"
        )
        self.efficiency_bar.setValue(int(min(100, max(0, ratio))))
        self.stats_pill.setText(f"{ratio:.0f}% 용량 절약")

    def _on_search_changed(self, text: str):
        self.filter_keyword = text.strip().lower()
        self._refresh_view()

    def _refresh_view(self):
        self.table.setRowCount(0)
        self.path_edit.setText("/" + (self.current_prefix + "/" if self.current_prefix else ""))

        self.back_btn.setEnabled(len(self.history) > 0)
        self.up_btn.setEnabled(bool(self.current_prefix))

        if not self.all_items:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("📂 열려 있는 아카이브가 없습니다. 상단 [열기 (Ctrl+O)]를 클릭하세요.")
            empty_item.setForeground(QColor("#94A3B8"))
            self.table.setItem(0, 0, empty_item)
            for col in range(1, 8):
                self.table.setItem(0, col, QTableWidgetItem(""))
            return

        row = 0
        # If searching, show all matching files across archive
        if self.filter_keyword:
            matches = [it for it in self.all_items if self.filter_keyword in it.name.lower()]
            if not matches:
                self.table.setRowCount(1)
                empty_item = QTableWidgetItem(f"🔍 '{self.filter_keyword}' 검색 결과가 없습니다.")
                empty_item.setForeground(QColor("#94A3B8"))
                self.table.setItem(0, 0, empty_item)
                for col in range(1, 8):
                    self.table.setItem(0, col, QTableWidgetItem(""))
                return
            for it in matches:
                self._insert_row(row, it, display_name=it.name)
                row += 1
            return

        # Normal directory drill-down
        prefix = self.current_prefix + "/" if self.current_prefix else ""
        prefix_len = len(prefix)

        if self.current_prefix:
            self.table.insertRow(row)
            up_item = QTableWidgetItem("📁 ..")
            up_item.setData(Qt.UserRole, ("..", True))
            self.table.setItem(row, 0, up_item)
            for col in range(1, 8):
                self.table.setItem(row, col, QTableWidgetItem(""))
            row += 1

        direct_items = {}
        for it in self.all_items:
            name = it.name
            if prefix and not name.startswith(prefix):
                continue
            rel = name[prefix_len:]
            parts = rel.split('/')

            if len(parts) == 1:
                direct_items[parts[0]] = (it, parts[0], it.is_dir)
            else:
                sub_dir_name = parts[0]
                if sub_dir_name not in direct_items:
                    folder_item = ArchiveItem(
                        name=prefix + sub_dir_name,
                        display_name=sub_dir_name,
                        is_dir=True,
                        original_size=0,
                        compressed_size=0,
                        ratio=0.0,
                        mtime=None,
                        crc="-",
                        is_encrypted=False,
                        kind="폴더"
                    )
                    direct_items[sub_dir_name] = (folder_item, sub_dir_name, True)

        sorted_keys = sorted(direct_items.keys(), key=lambda k: (not direct_items[k][2], k.lower()))

        for k in sorted_keys:
            it, disp, is_dir = direct_items[k]
            self._insert_row(row, it, display_name=it.display_name)
            row += 1

    def _get_type_badge(self, name: str, is_dir: bool) -> str:
        if is_dir:
            return "📁 "
        ext = os.path.splitext(name)[1].lower()
        if ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'):
            return "🖼️ "
        elif ext in ('.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.txt', '.md'):
            return "📄 "
        elif ext in ('.pdf', '.docx', '.xlsx', '.pptx', '.hwp'):
            return "📑 "
        elif ext in ('.zip', '.7z', '.tar', '.gz', '.rar'):
            return "📦 "
        elif ext in ('.mp3', '.wav', '.flac', '.mp4', '.mkv'):
            return "🎬 "
        elif ext in ('.exe', '.dll', '.bat', '.cmd'):
            return "⚙️ "
        return "📄 "

    def _insert_row(self, row: int, it: ArchiveItem, display_name: str):
        self.table.insertRow(row)

        icon_prefix = self._get_type_badge(display_name, it.is_dir)
        name_item = QTableWidgetItem(icon_prefix + display_name)
        name_item.setData(Qt.UserRole, (it.name, it.is_dir))
        self.table.setItem(row, 0, name_item)

        comp_str = format_bytes(it.compressed_size) if not it.is_dir else ""
        comp_item = QTableWidgetItem(comp_str)
        comp_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 1, comp_item)

        orig_str = format_bytes(it.original_size) if not it.is_dir else ""
        orig_item = QTableWidgetItem(orig_str)
        orig_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 2, orig_item)

        ratio_str = f"{it.ratio:.0f}%" if not it.is_dir and it.original_size > 0 else ""
        ratio_item = QTableWidgetItem(ratio_str)
        ratio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 3, ratio_item)

        kind_item = QTableWidgetItem(it.kind)
        self.table.setItem(row, 4, kind_item)

        date_str = ""
        if it.mtime:
            try:
                dt = datetime.datetime.fromtimestamp(it.mtime)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        date_item = QTableWidgetItem(date_str)
        self.table.setItem(row, 5, date_item)

        enc_str = "🔒 AES-256" if it.is_encrypted else "-"
        enc_item = QTableWidgetItem(enc_str)
        enc_item.setTextAlignment(Qt.AlignCenter)
        if it.is_encrypted:
            enc_item.setForeground(QColor("#D97706"))
        self.table.setItem(row, 6, enc_item)

        crc_item = QTableWidgetItem(it.crc)
        crc_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 7, crc_item)

    def _on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        path, is_dir = data

        if path == "..":
            self._go_up()
        elif is_dir:
            self.history.append(self.current_prefix)
            self.current_prefix = path
            self._refresh_view()
        else:
            self.item_double_clicked.emit(path, is_dir)

    def _go_up(self):
        if not self.current_prefix:
            return
        self.history.append(self.current_prefix)
        parts = self.current_prefix.split('/')
        self.current_prefix = '/'.join(parts[:-1]) if len(parts) > 1 else ""
        self._refresh_view()

    def _go_back(self):
        if self.history:
            self.current_prefix = self.history.pop()
            self._refresh_view()

    def _on_selection_changed(self):
        selected_rows = sorted(list(set(item.row() for item in self.table.selectedItems())))
        count = len(selected_rows)
        self.selection_changed.emit(count, 0)

        # 단일 파일 선택 시 실시간 이미지 미리보기 발송
        if count == 1:
            row = selected_rows[0]
            item = self.table.item(row, 0)
            if item:
                data = item.data(Qt.UserRole)
                if data and isinstance(data, tuple):
                    internal_path, is_dir = data
                    if not is_dir:
                        ext = os.path.splitext(internal_path)[1].lower()
                        if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.ico', '.svg'):
                            self.image_preview_requested.emit(internal_path)
                            return
                        else:
                            self.clear_image_preview("선택한 항목은\n이미지 파일이 아닙니다.")
                            self.img_info_lbl.setText(f"<b>파일명:</b> {os.path.basename(internal_path)}")
                            return
                    else:
                        self.clear_image_preview("선택한 항목은\n폴더입니다.")
                        return
        elif count == 0:
            self.clear_image_preview()

    def get_selected_items(self) -> List[str]:
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))
        targets = []
        for r in selected_rows:
            item = self.table.item(r, 0)
            if item:
                data = item.data(Qt.UserRole)
                if data and data[0] != "..":
                    targets.append(data[0])
        return targets

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        sel = self.get_selected_items()

        ext_action = QAction("📦 선택 항목 풀기...", self)
        ext_action.setEnabled(len(sel) > 0)
        ext_action.triggered.connect(lambda: self.extract_selected.emit(sel))
        menu.addAction(ext_action)

        menu.addSeparator()
        select_all_action = QAction("모두 선택 (Ctrl+A)", self)
        select_all_action.triggered.connect(self.table.selectAll)
        menu.addAction(select_all_action)

        menu.exec(self.table.mapToGlobal(pos))
