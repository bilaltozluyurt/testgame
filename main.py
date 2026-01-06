"""
UO Crafter - Main Application
Ultima Online crafting automation tool for VMware Fusion
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
from coordinate_manager import CoordinateManager
from automation_engine import AutomationEngine
from ocr_handler import OCRHandler
import pyautogui
pyautogui.FAILSAFE = False


class UOCrafterApp:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("UO Crafter")
        self.root.geometry("800x600")

        # Initialize managers
        self.coord_manager = CoordinateManager()
        self.automation = AutomationEngine(self.coord_manager)
        self.ocr_handler = OCRHandler(self.coord_manager)

        # Coordinate capture state
        self.capturing_coord_name = None
        self.countdown_window = None
        self.quick_capture_count = 0  # Counter for quick captures

        # Create UI
        self.create_ui()

        # Bind F8 for start/stop
        self.root.bind('<F8>', lambda e: self.toggle_automation())
        self.root.after(100, self.sync_ocr_settings)

    def sync_ocr_settings(self):
        """Pushes UI entry values into the OCR Handler on startup"""
        try:
            self.ocr_handler.capture_offset_x = int(self.capture_offset_x.get())
            self.ocr_handler.capture_offset_y = int(self.capture_offset_y.get())
            self.ocr_handler.capture_width = int(self.capture_width.get())
            self.ocr_handler.capture_height = int(self.capture_height.get())
        except:
            pass
        
    def create_ui(self):
        """Create the main UI with tabs"""
        # Create tab control
        self.tab_control = ttk.Notebook(self.root)

        # Create tabs
        self.tab_general = ttk.Frame(self.tab_control)
        self.tab_craft = ttk.Frame(self.tab_control)
        self.tab_kontrol = ttk.Frame(self.tab_control)
        self.tab_bitis = ttk.Frame(self.tab_control)
        self.tab_bod = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_general, text='Genel')
        self.tab_control.add(self.tab_craft, text='Craft')
        self.tab_control.add(self.tab_kontrol, text='Kontrol')
        self.tab_control.add(self.tab_bitis, text='Bitış')
        self.tab_control.add(self.tab_bod, text='BOD Toplama')

        self.tab_control.pack(expand=1, fill='both', padx=5, pady=5)

        # Build each tab
        self.build_general_tab()
        self.build_craft_tab()
        self.build_kontrol_tab()
        self.build_bitis_tab()
        self.build_bod_tab()

        # Status bar
        self.status_label = tk.Label(self.root, text="Hazır (Ready)", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Load saved coordinates into UI
        self.load_coordinates_to_ui()

        # Update VM status
        self.update_vm_status()

    def build_general_tab(self):
        """Build the General settings tab"""
        frame = tk.Frame(self.tab_general, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        # General Settings
        settings_group = tk.LabelFrame(frame, text="Genel Ayarlar", padx=10, pady=10)
        settings_group.pack(fill='x', pady=5)

        # Profile display (will be detected from VMware window)
        tk.Label(settings_group, text="Aktif Profil:").grid(row=0, column=0, sticky='w', pady=2)
        self.profile_label = tk.Label(settings_group, text="Algılanıyor...", fg="blue")
        self.profile_label.grid(row=0, column=1, columnspan=2, sticky='w', pady=2)

        # Keys configuration
        keys_group = tk.LabelFrame(frame, text="Tuşlar", padx=10, pady=10)
        keys_group.pack(fill='x', pady=5)

        tk.Label(keys_group, text="Düzenle:").grid(row=0, column=0, sticky='w')
        self.duzenle_entry = tk.Entry(keys_group, width=15)
        self.duzenle_entry.insert(0, self.coord_manager.hotkeys['duzenle'])
        self.duzenle_entry.grid(row=0, column=1, padx=5)

        tk.Label(keys_group, text="Kes:").grid(row=0, column=2, sticky='w', padx=(20, 0))
        self.kes_entry = tk.Entry(keys_group, width=15)
        self.kes_entry.insert(0, self.coord_manager.hotkeys['kes'])
        self.kes_entry.grid(row=0, column=3, padx=5)

        tk.Label(keys_group, text="Makrokliit:").grid(row=1, column=0, sticky='w', pady=5)
        self.makrokliit_entry = tk.Entry(keys_group, width=15)
        self.makrokliit_entry.insert(0, self.coord_manager.hotkeys['makrokliit'])
        self.makrokliit_entry.grid(row=1, column=1, padx=5, pady=5)

        # Starting item
        start_group = tk.LabelFrame(frame, text="İlk Start Ayan", padx=10, pady=10)
        start_group.pack(fill='x', pady=5)

        tk.Label(start_group, text="Başlangıç Item:").grid(row=0, column=0, sticky='w')
        self.starting_item = ttk.Combobox(start_group, width=20, values=["Oil Cloth", "Studded Gorget", "Furboots"])
        self.starting_item.set(self.coord_manager.settings['starting_item'])
        self.starting_item.grid(row=0, column=1, padx=5)

        tk.Label(start_group, text="Başlangıç Döngü No:").grid(row=1, column=0, sticky='w', pady=5)
        self.starting_cycle = tk.Entry(start_group, width=10)
        self.starting_cycle.insert(0, str(self.coord_manager.settings['starting_cycle']))
        self.starting_cycle.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # ImageSearch Tolerance
        tolerance_group = tk.LabelFrame(frame, text="ImageSearch Tolerance (0-255)", padx=10, pady=10)
        tolerance_group.pack(fill='x', pady=5)

        self.tolerance_var = tk.IntVar(value=self.coord_manager.settings['image_search_tolerance'])
        tolerance_scale = tk.Scale(tolerance_group, from_=0, to=255, orient=tk.HORIZONTAL,
                                    variable=self.tolerance_var, length=300)
        tolerance_scale.pack()

        # Crafting Automation Settings
        craft_settings = tk.LabelFrame(frame, text="Crafting Automation Settings", padx=10, pady=10)
        craft_settings.pack(fill='x', pady=5)

        # Interval setting (how many MX/MY clicks before D/S press)
        tk.Label(craft_settings, text="Items before D/S press:").grid(row=0, column=0, sticky='w')
        self.craft_interval = tk.Entry(craft_settings, width=8)
        self.craft_interval.insert(0, "60")  # Default: 30 items
        self.craft_interval.grid(row=0, column=1, padx=5)

        # D key setting
        tk.Label(craft_settings, text="D key (duzenle):").grid(row=0, column=2, sticky='w', padx=(20, 0))
        self.d_key = tk.Entry(craft_settings, width=8)
        self.d_key.insert(0, "d")  # Default: 'd'
        self.d_key.grid(row=0, column=3, padx=5)

        # S key setting
        tk.Label(craft_settings, text="S key (cutting):").grid(row=1, column=0, sticky='w', pady=5)
        self.s_key = tk.Entry(craft_settings, width=8)
        self.s_key.insert(0, "s")  # Default: 's'
        self.s_key.grid(row=1, column=1, padx=5, pady=5)

        # Click speed setting
        tk.Label(craft_settings, text="Click delay (ms):").grid(row=1, column=2, sticky='w', padx=(20, 0))
        self.click_delay = tk.Entry(craft_settings, width=8)
        self.click_delay.insert(0, "900")  # Default: 900ms
        self.click_delay.grid(row=1, column=3, padx=5)

        # Control buttons
        button_frame = tk.Frame(frame, pady=10)
        button_frame.pack(fill='x')

        self.start_button = tk.Button(button_frame, text="F8: Start/Stop", command=self.toggle_automation,
                                       bg='#28a745', fg='white', font=('Arial', 12, 'bold'),
                                       width=15, height=2, relief='raised', borderwidth=2)
        self.start_button.pack(side='left', padx=5)

        tk.Button(button_frame, text="F7: Kaydet (Save)", command=self.save_settings,
                  bg='#007bff', fg='white', font=('Arial', 10), width=15,
                  relief='raised', borderwidth=2).pack(side='left', padx=5)

        # VM Status
        self.vm_status_label = tk.Label(frame, text="VM Durumu: Kontrol ediliyor...", font=('Arial', 10))
        self.vm_status_label.pack(pady=10)

    def build_craft_tab(self):
        """Build the Craft coordinates tab"""
        frame = tk.Frame(self.tab_craft, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        # Craft Coordinates
        coord_group = tk.LabelFrame(frame, text="Craft Koordinatları (CLIENT coords)", padx=10, pady=10)
        coord_group.pack(fill='x', pady=5)

        # Kesilecek Item (used in D/S sequence every N items)
        tk.Label(coord_group, text="Kesilecek Item:").grid(row=0, column=0, sticky='w', pady=5)
        self.kesilecek_x = tk.Entry(coord_group, width=10)
        self.kesilecek_x.grid(row=0, column=1, padx=2, pady=5)
        self.kesilecek_y = tk.Entry(coord_group, width=10)
        self.kesilecek_y.grid(row=0, column=2, padx=2, pady=5)
        tk.Button(coord_group, text="Seç", command=lambda: self.start_coord_capture('kesilecek_item', self.kesilecek_x, self.kesilecek_y)).grid(row=0, column=3, padx=5, pady=5)

        # Kesilecek Item for Oil Cloth (specific position for oil cloth cutting)
        tk.Label(coord_group, text="Kesilecek (Oil Cloth):").grid(row=1, column=0, sticky='w', pady=5)
        self.kesilecek_oilcloth_x = tk.Entry(coord_group, width=10)
        self.kesilecek_oilcloth_x.grid(row=1, column=1, padx=2, pady=5)
        self.kesilecek_oilcloth_y = tk.Entry(coord_group, width=10)
        self.kesilecek_oilcloth_y.grid(row=1, column=2, padx=2, pady=5)
        tk.Button(coord_group, text="Seç", command=lambda: self.start_coord_capture('kesilecek_item_oilcloth', self.kesilecek_oilcloth_x, self.kesilecek_oilcloth_y)).grid(row=1, column=3, padx=5, pady=5)

        # Debug button for VMware window detection
        debug_frame = tk.Frame(coord_group)
        debug_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky='w')
        tk.Button(debug_frame, text="🔍 Debug VMware Window",
                 command=self.debug_vmware_window,
                 bg='#17a2b8', fg='white', font=('Arial', 9)).pack(side='left', padx=5)

        # Item Settings
        items_group = tk.LabelFrame(frame, text="Item Ayarları (Grup / Make / Adet)", padx=10, pady=10)
        items_group.pack(fill='x', pady=5)

        # Headers
        tk.Label(items_group, text="", width=12).grid(row=0, column=0)
        tk.Label(items_group, text="Gx").grid(row=0, column=1)
        tk.Label(items_group, text="Gy").grid(row=0, column=2)
        tk.Label(items_group, text="Mx").grid(row=0, column=3)
        tk.Label(items_group, text="My").grid(row=0, column=4)
        tk.Label(items_group, text="Adet").grid(row=0, column=5)

        # Load coordinates and counts from config
        # get_coordinate returns (x, y) tuple or None
        furboots_group = self.coord_manager.get_coordinate('furboots_group')
        furboots_make = self.coord_manager.get_coordinate('furboots_make')
        furboots_count = self.coord_manager.settings.get('furboots_count', '')

        oil_cloth_group = self.coord_manager.get_coordinate('oil_cloth_group')
        oil_cloth_make = self.coord_manager.get_coordinate('oil_cloth_make')
        oil_cloth_count = self.coord_manager.settings.get('oil_cloth_count', '')

        studded_gorget_group = self.coord_manager.get_coordinate('studded_gorget_group')
        studded_gorget_make = self.coord_manager.get_coordinate('studded_gorget_make')
        studded_gorget_count = self.coord_manager.settings.get('studded_gorget_count', '')

        # Furboots
        self.create_item_row(items_group, "Furboots:", 1, "furboots",
                            furboots_group[0] if furboots_group else "",
                            furboots_group[1] if furboots_group else "",
                            furboots_make[0] if furboots_make else "",
                            furboots_make[1] if furboots_make else "",
                            furboots_count)

        # Oil Cloth
        self.create_item_row(items_group, "Oil Cloth:", 2, "oil_cloth",
                            oil_cloth_group[0] if oil_cloth_group else "",
                            oil_cloth_group[1] if oil_cloth_group else "",
                            oil_cloth_make[0] if oil_cloth_make else "",
                            oil_cloth_make[1] if oil_cloth_make else "",
                            oil_cloth_count)

        # Studded Gorget
        self.create_item_row(items_group, "Studded Gorget:", 3, "studded_gorget",
                            studded_gorget_group[0] if studded_gorget_group else "",
                            studded_gorget_group[1] if studded_gorget_group else "",
                            studded_gorget_make[0] if studded_gorget_make else "",
                            studded_gorget_make[1] if studded_gorget_make else "",
                            studded_gorget_count)

        # Save button
        tk.Button(frame, text="Kaydet (Save)", command=self.save_settings,
                  bg='#28a745', fg='white', font=('Arial', 10), width=15,
                  relief='raised', borderwidth=2, pady=5).pack(pady=10)

    def create_item_row(self, parent, label, row, item_name, gx_val, gy_val, mx_val, my_val, count_val):
        """Helper to create an item configuration row with Seç buttons"""
        tk.Label(parent, text=label).grid(row=row, column=0, sticky='w', pady=2)

        gx = tk.Entry(parent, width=8)
        if gx_val:
            gx.insert(0, str(gx_val))
        gx.grid(row=row, column=1, padx=2, pady=2)

        gy = tk.Entry(parent, width=8)
        if gy_val:
            gy.insert(0, str(gy_val))
        gy.grid(row=row, column=2, padx=2, pady=2)

        # Seç button for Gx, Gy (Group coordinates)
        tk.Button(parent, text="Seç", width=4,
                  command=lambda: self.start_coord_capture(f'{item_name}_group', gx, gy)).grid(row=row, column=3, padx=2, pady=2)

        mx = tk.Entry(parent, width=8)
        if mx_val:
            mx.insert(0, str(mx_val))
        mx.grid(row=row, column=4, padx=2, pady=2)

        my = tk.Entry(parent, width=8)
        if my_val:
            my.insert(0, str(my_val))
        my.grid(row=row, column=5, padx=2, pady=2)

        # Seç button for Mx, My (Make/item coordinates)
        tk.Button(parent, text="Seç", width=4,
                  command=lambda: self.start_coord_capture(f'{item_name}_make', mx, my)).grid(row=row, column=6, padx=2, pady=2)

        count = tk.Entry(parent, width=8)
        if count_val:
            count.insert(0, str(count_val))
        count.grid(row=row, column=7, padx=2, pady=2)

        # Store references
        setattr(self, f'{item_name}_gx', gx)
        setattr(self, f'{item_name}_gy', gy)
        setattr(self, f'{item_name}_mx', mx)
        setattr(self, f'{item_name}_my', my)
        setattr(self, f'{item_name}_count', count)

    def build_kontrol_tab(self):
        """Build the Kontrol tab for Makro Kontrolü popup handling"""
        # Create a canvas with scrollbar for Kontrol tab
        canvas = tk.Canvas(self.tab_kontrol)
        scrollbar = tk.Scrollbar(self.tab_kontrol, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, padx=10, pady=10)

        scrollable_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Use scrollable_frame instead of frame for all widgets
        frame = scrollable_frame

        # Info
        info_label = tk.Label(frame,
                              text="Makro Kontrolü popup'ı otomatik olarak handle edilir.\n"
                                   "Popup her zaman aynı yerde çıkar, koordinatları kaydedin.",
                              font=('Arial', 11), justify='left')
        info_label.pack(pady=10)

        # Makro Kontrolü coordinates
        makro_group = tk.LabelFrame(frame, text="Makro Kontrolü Popup Koordinatları", padx=10, pady=10)
        makro_group.pack(fill='x', pady=5)

        # Textbox (for detection)
        tk.Label(makro_group, text="Textbox (soru alanı):").grid(row=0, column=0, sticky='w', pady=5)
        self.textbox_x = tk.Entry(makro_group, width=10)
        self.textbox_x.grid(row=0, column=1, padx=2, pady=5)
        self.textbox_y = tk.Entry(makro_group, width=10)
        self.textbox_y.grid(row=0, column=2, padx=2, pady=5)
        tk.Button(makro_group, text="Seç",
                  command=lambda: self.start_coord_capture('textbox', self.textbox_x, self.textbox_y)).grid(row=0, column=3, padx=5, pady=5)

        # Kontrol Et button
        tk.Label(makro_group, text="Kontrol Et butonu:").grid(row=1, column=0, sticky='w', pady=5)
        self.kontrol_et_x = tk.Entry(makro_group, width=10)
        self.kontrol_et_x.grid(row=1, column=1, padx=2, pady=5)
        self.kontrol_et_y = tk.Entry(makro_group, width=10)
        self.kontrol_et_y.grid(row=1, column=2, padx=2, pady=5)
        tk.Button(makro_group, text="Seç",
                  command=lambda: self.start_coord_capture('kontrol_et', self.kontrol_et_x, self.kontrol_et_y)).grid(row=1, column=3, padx=5, pady=5)

        # Close/Cancel button (X or Iptal)
        tk.Label(makro_group, text="Kapat (X) butonu (opsiyonel):").grid(row=2, column=0, sticky='w', pady=5)
        self.kapat_x = tk.Entry(makro_group, width=10)
        self.kapat_x.grid(row=2, column=1, padx=2, pady=5)
        self.kapat_y = tk.Entry(makro_group, width=10)
        self.kapat_y.grid(row=2, column=2, padx=2, pady=5)
        tk.Button(makro_group, text="Seç",
                  command=lambda: self.start_coord_capture('kapat', self.kapat_x, self.kapat_y)).grid(row=2, column=3, padx=5, pady=5)

        # Popup bounds detection (NEW - Faster detection)
        bounds_group = tk.LabelFrame(frame, text="Popup Sınırları (Hızlı Tespit İçin - Önerilen)", padx=10, pady=10)
        bounds_group.pack(fill='x', pady=5)

        tk.Label(bounds_group, text="Popup açıkken sol üst ve sağ alt köşeleri seçin.\n"
                                     "Bu sayede popup tespiti çok daha hızlı olur (mouse hareketi yok).",
                 font=('Arial', 9), fg='gray', justify='left').pack(anchor='w', pady=5)

        # Create inner frame for grid layout
        bounds_inner = tk.Frame(bounds_group)
        bounds_inner.pack(fill='x', pady=5)

        # Top-left corner
        tk.Label(bounds_inner, text="Sol Üst Köşe:").grid(row=0, column=0, sticky='w', pady=5)
        self.popup_tl_x = tk.Entry(bounds_inner, width=10)
        self.popup_tl_x.grid(row=0, column=1, padx=2, pady=5)
        self.popup_tl_y = tk.Entry(bounds_inner, width=10)
        self.popup_tl_y.grid(row=0, column=2, padx=2, pady=5)
        tk.Button(bounds_inner, text="Seç",
                  command=lambda: self.start_coord_capture('popup_top_left', self.popup_tl_x, self.popup_tl_y)).grid(row=0, column=3, padx=5, pady=5)

        # Bottom-right corner
        tk.Label(bounds_inner, text="Sağ Alt Köşe:").grid(row=1, column=0, sticky='w', pady=5)
        self.popup_br_x = tk.Entry(bounds_inner, width=10)
        self.popup_br_x.grid(row=1, column=1, padx=2, pady=5)
        self.popup_br_y = tk.Entry(bounds_inner, width=10)
        self.popup_br_y.grid(row=1, column=2, padx=2, pady=5)
        tk.Button(bounds_inner, text="Seç",
                  command=lambda: self.start_coord_capture('popup_bottom_right', self.popup_br_x, self.popup_br_y)).grid(row=1, column=3, padx=5, pady=5)

        # Result region (fail/success message detection)
        result_group = tk.LabelFrame(frame, text="Sonuç Mesajı Bölgesi (Başarı/Başarısız Kontrolü)", padx=10, pady=10)
        result_group.pack(fill='x', pady=5)

        tk.Label(result_group, text="Başarı/başarısız mesajının göründüğü alanın sol üst ve sağ alt köşeleri.\n"
                                     "Eğer yanlış cevap verirseniz, 'M' tuşuna basıp tekrar deneyecek.",
                 font=('Arial', 9), fg='gray', justify='left').pack(anchor='w', pady=5)

        # Create inner frame for grid layout
        result_inner = tk.Frame(result_group)
        result_inner.pack(fill='x', pady=5)

        # Result top-left corner
        tk.Label(result_inner, text="Sol Üst Köşe:").grid(row=0, column=0, sticky='w', pady=5)
        self.result_tl_x = tk.Entry(result_inner, width=10)
        self.result_tl_x.grid(row=0, column=1, padx=2, pady=5)
        self.result_tl_y = tk.Entry(result_inner, width=10)
        self.result_tl_y.grid(row=0, column=2, padx=2, pady=5)
        tk.Button(result_inner, text="Seç",
                  command=lambda: self.start_coord_capture('result_top_left', self.result_tl_x, self.result_tl_y)).grid(row=0, column=3, padx=5, pady=5)

        # Result bottom-right corner
        tk.Label(result_inner, text="Sağ Alt Köşe:").grid(row=1, column=0, sticky='w', pady=5)
        self.result_br_x = tk.Entry(result_inner, width=10)
        self.result_br_x.grid(row=1, column=1, padx=2, pady=5)
        self.result_br_y = tk.Entry(result_inner, width=10)
        self.result_br_y.grid(row=1, column=2, padx=2, pady=5)
        tk.Button(result_inner, text="Seç",
                  command=lambda: self.start_coord_capture('result_bottom_right', self.result_br_x, self.result_br_y)).grid(row=1, column=3, padx=5, pady=5)

        # M key (for retry - keyboard press like D/S)
        tk.Label(result_inner, text="M Tuşu (manuel retry için):").grid(row=2, column=0, sticky='w', pady=5)
        self.m_key_entry = tk.Entry(result_inner, width=10)
        self.m_key_entry.insert(0, "m")  # Default: m key
        self.m_key_entry.grid(row=2, column=1, padx=2, pady=5)
        tk.Label(result_inner, text="(Başarısız olursa bu tuşa basılır)",
                 font=('Arial', 8), fg='gray').grid(row=2, column=2, columnspan=2, sticky='w', padx=5)

        # Settings
        settings_group = tk.LabelFrame(frame, text="Makro Kontrolü Ayarları", padx=10, pady=10)
        settings_group.pack(fill='x', pady=5)

        self.auto_handle_makro = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_group, text="Makro Kontrolü popup'ını otomatik handle et",
                       variable=self.auto_handle_makro).pack(anchor='w', pady=5)

        # OCR/Image Search toggle
        self.use_image_search = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_group, text="Image search kullan (soruyu resimlere bakarak bul)",
                       variable=self.use_image_search).pack(anchor='w', pady=5)

        # Auto-save unknown questions
        self.auto_save_questions = tk.BooleanVar(value=False)
        auto_save_cb = tk.Checkbutton(settings_group,
                                      text="Bilinmeyen soruları otomatik kaydet (auto_001.png, auto_002.png...)",
                                      variable=self.auto_save_questions,
                                      command=self.toggle_auto_save)
        auto_save_cb.pack(anchor='w', pady=5)

        # Capture region offset adjustments
        offset_group = tk.LabelFrame(frame, text="Yakalama Bölgesi Ayarları", padx=10, pady=10)
        offset_group.pack(fill='x', pady=5)

        tk.Label(offset_group, text="Panel hareket ederse bu değerlerle yakalama bölgesini ayarlayın:",
                 font=('Arial', 9), fg='gray').pack(anchor='w', pady=2)

        # X offset
        offset_x_frame = tk.Frame(offset_group)
        offset_x_frame.pack(anchor='w', pady=2)
        tk.Label(offset_x_frame, text="X offset (sol/sağ):").pack(side='left', padx=5)
        self.capture_offset_x = tk.Entry(offset_x_frame, width=8)
        self.capture_offset_x.insert(0, "-55")  # Default: -100 for 200px width
        self.capture_offset_x.pack(side='left', padx=5)
        tk.Label(offset_x_frame, text="(negatif = sola, pozitif = sağa)",
                 font=('Arial', 8), fg='gray').pack(side='left')

        # Y offset
        offset_y_frame = tk.Frame(offset_group)
        offset_y_frame.pack(anchor='w', pady=2)
        tk.Label(offset_y_frame, text="Y offset (yukarı/aşağı):").pack(side='left', padx=5)
        self.capture_offset_y = tk.Entry(offset_y_frame, width=8)
        self.capture_offset_y.insert(0, "-47")  # Default
        self.capture_offset_y.pack(side='left', padx=5)
        tk.Label(offset_y_frame, text="(negatif = yukarı, pozitif = aşağı)",
                 font=('Arial', 8), fg='gray').pack(side='left')

        # Width and Height
        size_frame = tk.Frame(offset_group)
        size_frame.pack(anchor='w', pady=2)
        tk.Label(size_frame, text="Genişlik:").pack(side='left', padx=5)
        self.capture_width = tk.Entry(size_frame, width=8)
        self.capture_width.insert(0, "200")  # Default: 200px to match friend's images
        self.capture_width.pack(side='left', padx=5)
        tk.Label(size_frame, text="Yükseklik:").pack(side='left', padx=10)
        self.capture_height = tk.Entry(size_frame, width=8)
        self.capture_height.insert(0, "20")  # Default: 20px to match friend's images
        self.capture_height.pack(side='left', padx=5)

        # Apply button
        tk.Button(offset_group, text="Değişiklikleri Uygula ve Overlay Göster",
                  command=self.apply_and_show_overlay,
                  bg='#28a745', fg='white', font=('Arial', 9),
                  relief='raised', borderwidth=2).pack(pady=5)

        # Quick capture mode
        capture_group = tk.LabelFrame(frame, text="Hızlı Yakalama Modu", padx=10, pady=10)
        capture_group.pack(fill='x', pady=5)

        tk.Label(capture_group,
                text="Popup açıkken bu butona bas - otomatik numara ile kaydeder (capture_001.png, capture_002.png...)",
                font=('Arial', 9), fg='blue', wraplength=700, justify='left').pack(anchor='w', pady=2)

        tk.Button(capture_group, text="📸 HIZLI YAKALA (Popup Açık Olmalı)",
                 command=self.quick_capture,
                 bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold'),
                 relief='raised', borderwidth=3, height=2).pack(pady=10, fill='x')

        self.capture_counter_label = tk.Label(capture_group, text="Kaydedilen: 0",
                                             font=('Arial', 10, 'bold'), fg='green')
        self.capture_counter_label.pack(pady=2)     

        # Test buttons
        test_frame = tk.Frame(frame, pady=10)
        test_frame.pack()

        tk.Button(test_frame, text="Test: Soru Bölgesini Göster", command=self.test_question_region,
                  bg='#6c757d', fg='white', font=('Arial', 10), width=25,
                  relief='raised', borderwidth=2).pack(pady=5)

        tk.Button(test_frame, text="Yakalama Bölgesini Göster (Overlay)", command=self.show_capture_overlay,
                  bg='#17a2b8', fg='white', font=('Arial', 10), width=25,
                  relief='raised', borderwidth=2).pack(pady=5)

        tk.Button(test_frame, text="Test: Sonuç Mesajı Kontrolü", command=self.test_result_detection,
                  bg='#28a745', fg='white', font=('Arial', 10), width=25,
                  relief='raised', borderwidth=2).pack(pady=5)

    def build_bitis_tab(self):
        """Build the Bitış (Finish) tab"""
        frame = tk.Frame(self.tab_bitis, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        # Makas coordinate
        makas_group = tk.LabelFrame(frame, text="Makas (Double-Click)", padx=10, pady=10)
        makas_group.pack(fill='x', pady=5)

        tk.Label(makas_group, text="Makas Konumu (X, Y):").grid(row=0, column=0, sticky='w', pady=5)
        self.makas_x = tk.Entry(makas_group, width=10)
        self.makas_x.grid(row=0, column=1, padx=5)
        self.makas_y = tk.Entry(makas_group, width=10)
        self.makas_y.grid(row=0, column=2, padx=5)
        tk.Button(makas_group, text="Seç", command=lambda: self.start_coord_capture('makas', self.makas_x, self.makas_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        # K key setting
        k_key_group = tk.LabelFrame(frame, text="Ambar Ayarları", padx=10, pady=10)
        k_key_group.pack(fill='x', pady=5)
        tk.Label(k_key_group, text="K key (Ambar):").grid(row=0, column=0, sticky='w')
        self.k_key = tk.Entry(k_key_group, width=10)
        self.k_key.insert(0, "k")
        self.k_key.grid(row=0, column=1, padx=5)

        # Kaynak Ekle button
        kaynak_ekle_group = tk.LabelFrame(frame, text="Kaynak Ekle Button", padx=10, pady=10)
        kaynak_ekle_group.pack(fill='x', pady=5)
        tk.Label(kaynak_ekle_group, text="Kaynak Ekle (X, Y):").grid(row=0, column=0, sticky='w')
        self.kaynak_ekle_x = tk.Entry(kaynak_ekle_group, width=10)
        self.kaynak_ekle_x.grid(row=0, column=1, padx=5)
        self.kaynak_ekle_y = tk.Entry(kaynak_ekle_group, width=10)
        self.kaynak_ekle_y.grid(row=0, column=2, padx=5)
        tk.Button(kaynak_ekle_group, text="Seç", command=lambda: self.start_coord_capture('kaynak_ekle', self.kaynak_ekle_x, self.kaynak_ekle_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        # 3 click locations
        click_locations_group = tk.LabelFrame(frame, text="3 Locations (Bandage & Resources)", padx=10, pady=10)
        click_locations_group.pack(fill='x', pady=5)

        tk.Label(click_locations_group, text="Location 1 (X, Y):").grid(row=0, column=0, sticky='w')
        self.ambar_loc1_x = tk.Entry(click_locations_group, width=10)
        self.ambar_loc1_x.grid(row=0, column=1, padx=5)
        self.ambar_loc1_y = tk.Entry(click_locations_group, width=10)
        self.ambar_loc1_y.grid(row=0, column=2, padx=5)
        tk.Button(click_locations_group, text="Seç", command=lambda: self.start_coord_capture('ambar_loc1', self.ambar_loc1_x, self.ambar_loc1_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        tk.Label(click_locations_group, text="Location 2 (X, Y):").grid(row=1, column=0, sticky='w')
        self.ambar_loc2_x = tk.Entry(click_locations_group, width=10)
        self.ambar_loc2_x.grid(row=1, column=1, padx=5)
        self.ambar_loc2_y = tk.Entry(click_locations_group, width=10)
        self.ambar_loc2_y.grid(row=1, column=2, padx=5)
        tk.Button(click_locations_group, text="Seç", command=lambda: self.start_coord_capture('ambar_loc2', self.ambar_loc2_x, self.ambar_loc2_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=1, column=3, padx=5)

        tk.Label(click_locations_group, text="Location 3 (X, Y):").grid(row=2, column=0, sticky='w')
        self.ambar_loc3_x = tk.Entry(click_locations_group, width=10)
        self.ambar_loc3_x.grid(row=2, column=1, padx=5)
        self.ambar_loc3_y = tk.Entry(click_locations_group, width=10)
        self.ambar_loc3_y.grid(row=2, column=2, padx=5)
        tk.Button(click_locations_group, text="Seç", command=lambda: self.start_coord_capture('ambar_loc3', self.ambar_loc3_x, self.ambar_loc3_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=2, column=3, padx=5)

        # Cloth button
        cloth_button_group = tk.LabelFrame(frame, text="Cloth Button", padx=10, pady=10)
        cloth_button_group.pack(fill='x', pady=5)
        tk.Label(cloth_button_group, text="Cloth Button (X, Y):").grid(row=0, column=0, sticky='w')
        self.cloth_button_x = tk.Entry(cloth_button_group, width=10)
        self.cloth_button_x.grid(row=0, column=1, padx=5)
        self.cloth_button_y = tk.Entry(cloth_button_group, width=10)
        self.cloth_button_y.grid(row=0, column=2, padx=5)
        tk.Button(cloth_button_group, text="Seç", command=lambda: self.start_coord_capture('cloth_button', self.cloth_button_x, self.cloth_button_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        # Leather button
        leather_button_group = tk.LabelFrame(frame, text="Leather Button", padx=10, pady=10)
        leather_button_group.pack(fill='x', pady=5)
        tk.Label(leather_button_group, text="Leather Button (X, Y):").grid(row=0, column=0, sticky='w')
        self.leather_button_x = tk.Entry(leather_button_group, width=10)
        self.leather_button_x.grid(row=0, column=1, padx=5)
        self.leather_button_y = tk.Entry(leather_button_group, width=10)
        self.leather_button_y.grid(row=0, column=2, padx=5)
        tk.Button(leather_button_group, text="Seç", command=lambda: self.start_coord_capture('leather_button', self.leather_button_x, self.leather_button_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        # Kaynak Çıkar popup
        kaynak_cikar_group = tk.LabelFrame(frame, text="Kaynak Çıkar Popup (Shared)", padx=10, pady=10)
        kaynak_cikar_group.pack(fill='x', pady=5)

        tk.Label(kaynak_cikar_group, text="Text Field (X, Y):").grid(row=0, column=0, sticky='w')
        self.istenilen_miktar_x = tk.Entry(kaynak_cikar_group, width=10)
        self.istenilen_miktar_x.grid(row=0, column=1, padx=5)
        self.istenilen_miktar_y = tk.Entry(kaynak_cikar_group, width=10)
        self.istenilen_miktar_y.grid(row=0, column=2, padx=5)
        tk.Button(kaynak_cikar_group, text="Seç", command=lambda: self.start_coord_capture('istenilen_miktar', self.istenilen_miktar_x, self.istenilen_miktar_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=0, column=3, padx=5)

        tk.Label(kaynak_cikar_group, text="Cloth Amount:").grid(row=1, column=0, sticky='w')
        self.cloth_amount = tk.Entry(kaynak_cikar_group, width=10)
        self.cloth_amount.insert(0, "5201")
        self.cloth_amount.grid(row=1, column=1, padx=5)

        tk.Label(kaynak_cikar_group, text="Leather Amount:").grid(row=2, column=0, sticky='w')
        self.leather_amount = tk.Entry(kaynak_cikar_group, width=10)
        self.leather_amount.insert(0, "838")
        self.leather_amount.grid(row=2, column=1, padx=5)

        tk.Label(kaynak_cikar_group, text="Çantaya Button (X, Y):").grid(row=3, column=0, sticky='w')
        self.cantaya_x = tk.Entry(kaynak_cikar_group, width=10)
        self.cantaya_x.grid(row=3, column=1, padx=5)
        self.cantaya_y = tk.Entry(kaynak_cikar_group, width=10)
        self.cantaya_y.grid(row=3, column=2, padx=5)
        tk.Button(kaynak_cikar_group, text="Seç", command=lambda: self.start_coord_capture('cantaya', self.cantaya_x, self.cantaya_y),
                  bg='#007bff', fg='white', font=('Arial', 9), width=8).grid(row=3, column=3, padx=5)

        # Save button
        tk.Button(frame, text="F7: Kaydet (Save)", command=self.save_settings,
                  bg='#007bff', fg='white', font=('Arial', 10), width=15,
                  relief='raised', borderwidth=2).pack(pady=10)

    def build_bod_tab(self):
        """Build the BOD Toplama (BOD Collection) tab"""
        # Create a canvas with scrollbar for BOD tab
        canvas = tk.Canvas(self.tab_bod)
        scrollbar = tk.Scrollbar(self.tab_bod, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, padx=10, pady=10)

        scrollable_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scrollable_frame

        # Info
        info_label = tk.Label(frame,
                              text="BOD Collection System - Collects 50-skill BODs after Ambar completes\n"
                                   "Configure coordinates for 20 BOD slots (10 left + 10 right)",
                              font=('Arial', 11), justify='left', fg='blue')
        info_label.pack(pady=10)

        # Enable/Disable BOD Collection
        settings_group = tk.LabelFrame(frame, text="BOD Collection Settings", padx=10, pady=10)
        settings_group.pack(fill='x', pady=5)

        self.enable_bod_collection = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_group, text="Enable BOD Collection (after Ambar completes)",
                       variable=self.enable_bod_collection, font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w', pady=5)

        # F key setting
        tk.Label(settings_group, text="F key (opens BOD dialog):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.f_key = tk.Entry(settings_group, width=10)
        self.f_key.insert(0, "f")
        self.f_key.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Start slot setting
        tk.Label(settings_group, text="Start from slot (1-20):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.start_bod_slot = tk.Entry(settings_group, width=10)
        self.start_bod_slot.insert(0, "1")
        self.start_bod_slot.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        tk.Label(settings_group, text="(Manual override - auto-increments after each cycle)",
                 font=('Arial', 8), fg='gray').grid(row=2, column=2, sticky='w', padx=5)

        # Current slot and page offset (editable with reset button)
        tk.Label(settings_group, text="Current slot:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.current_bod_slot_entry = tk.Entry(settings_group, width=10)
        self.current_bod_slot_entry.insert(0, "1")
        self.current_bod_slot_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        tk.Button(settings_group, text="Update", width=8,
                  command=self.update_current_slot,
                  bg='#ffc107', fg='black', font=('Arial', 8)).grid(row=3, column=2, padx=5, pady=5)
        tk.Label(settings_group, text="(Manually adjust if needed)",
                 font=('Arial', 8), fg='gray').grid(row=3, column=3, sticky='w', padx=5)

        tk.Label(settings_group, text="Page offset:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.page_offset_entry = tk.Entry(settings_group, width=10)
        self.page_offset_entry.insert(0, "0")
        self.page_offset_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        tk.Button(settings_group, text="Update", width=8,
                  command=self.update_page_offset,
                  bg='#ffc107', fg='black', font=('Arial', 8)).grid(row=4, column=2, padx=5, pady=5)
        tk.Label(settings_group, text="(Sonraki clicks = 3 + page_offset)",
                 font=('Arial', 8), fg='gray').grid(row=4, column=3, sticky='w', padx=5)

        # Control coordinates
        control_group = tk.LabelFrame(frame, text="BOD Dialog Coordinates", padx=10, pady=10)
        control_group.pack(fill='x', pady=5)

        # Close Ambar (right-click)
        tk.Label(control_group, text="Close Ambar (right-click):").grid(row=0, column=0, sticky='w', pady=5)
        self.close_ambar_x = tk.Entry(control_group, width=10)
        self.close_ambar_x.grid(row=0, column=1, padx=2, pady=5)
        self.close_ambar_y = tk.Entry(control_group, width=10)
        self.close_ambar_y.grid(row=0, column=2, padx=2, pady=5)
        tk.Button(control_group, text="Seç",
                  command=lambda: self.start_coord_capture('close_ambar', self.close_ambar_x, self.close_ambar_y)).grid(row=0, column=3, padx=5, pady=5)

        # Bod Hakları button
        tk.Label(control_group, text="Bod Hakları button:").grid(row=1, column=0, sticky='w', pady=5)
        self.bod_haklari_x = tk.Entry(control_group, width=10)
        self.bod_haklari_x.grid(row=1, column=1, padx=2, pady=5)
        self.bod_haklari_y = tk.Entry(control_group, width=10)
        self.bod_haklari_y.grid(row=1, column=2, padx=2, pady=5)
        tk.Button(control_group, text="Seç",
                  command=lambda: self.start_coord_capture('bod_haklari_button', self.bod_haklari_x, self.bod_haklari_y)).grid(row=1, column=3, padx=5, pady=5)

        # Sonraki button
        tk.Label(control_group, text="Sonraki button:").grid(row=2, column=0, sticky='w', pady=5)
        self.sonraki_button_x = tk.Entry(control_group, width=10)
        self.sonraki_button_x.grid(row=2, column=1, padx=2, pady=5)
        self.sonraki_button_y = tk.Entry(control_group, width=10)
        self.sonraki_button_y.grid(row=2, column=2, padx=2, pady=5)
        tk.Button(control_group, text="Seç",
                  command=lambda: self.start_coord_capture('sonraki_button', self.sonraki_button_x, self.sonraki_button_y)).grid(row=2, column=3, padx=5, pady=5)

        # Popup close (right-click after BOD selection)
        tk.Label(control_group, text="Popup close (right-click):").grid(row=3, column=0, sticky='w', pady=5)
        self.popup_close_x = tk.Entry(control_group, width=10)
        self.popup_close_x.grid(row=3, column=1, padx=2, pady=5)
        self.popup_close_y = tk.Entry(control_group, width=10)
        self.popup_close_y.grid(row=3, column=2, padx=2, pady=5)
        tk.Button(control_group, text="Seç",
                  command=lambda: self.start_coord_capture('popup_close', self.popup_close_x, self.popup_close_y)).grid(row=3, column=3, padx=5, pady=5)

        # 20 BOD Slots
        bod_slots_group = tk.LabelFrame(frame, text="20 BOD Slot Coordinates (10 Left + 10 Right)", padx=10, pady=10)
        bod_slots_group.pack(fill='x', pady=5)

        # Create storage for entry widgets
        self.bod_slot_entries = {}

        # Left side (slots 1-10)
        left_frame = tk.LabelFrame(bod_slots_group, text="Left Side (Slots 1-10)", padx=5, pady=5)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky='n')

        for i in range(1, 11):
            row_frame = tk.Frame(left_frame)
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=f"Slot {i}:", width=8).pack(side='left', padx=2)
            x_entry = tk.Entry(row_frame, width=8)
            x_entry.pack(side='left', padx=2)
            y_entry = tk.Entry(row_frame, width=8)
            y_entry.pack(side='left', padx=2)
            tk.Button(row_frame, text="Seç", width=4,
                      command=lambda slot=i, x=x_entry, y=y_entry: self.start_coord_capture(f'bod_slot_{slot}', x, y)).pack(side='left', padx=2)

            self.bod_slot_entries[i] = (x_entry, y_entry)

        # Right side (slots 11-20)
        right_frame = tk.LabelFrame(bod_slots_group, text="Right Side (Slots 11-20)", padx=5, pady=5)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky='n')

        for i in range(11, 21):
            row_frame = tk.Frame(right_frame)
            row_frame.pack(fill='x', pady=2)

            tk.Label(row_frame, text=f"Slot {i}:", width=8).pack(side='left', padx=2)
            x_entry = tk.Entry(row_frame, width=8)
            x_entry.pack(side='left', padx=2)
            y_entry = tk.Entry(row_frame, width=8)
            y_entry.pack(side='left', padx=2)
            tk.Button(row_frame, text="Seç", width=4,
                      command=lambda slot=i, x=x_entry, y=y_entry: self.start_coord_capture(f'bod_slot_{slot}', x, y)).pack(side='left', padx=2)

            self.bod_slot_entries[i] = (x_entry, y_entry)

        # Save button
        tk.Button(frame, text="F7: Kaydet (Save)", command=self.save_settings,
                  bg='#28a745', fg='white', font=('Arial', 10), width=15,
                  relief='raised', borderwidth=2).pack(pady=10)

    def start_coord_capture(self, coord_name, x_entry, y_entry):
        """Start coordinate capture process with countdown"""
        self.capturing_coord_name = coord_name
        self.capturing_x_entry = x_entry
        self.capturing_y_entry = y_entry

        # Minimize main window
        self.root.iconify()

        # Show countdown window
        self.show_countdown()

    def show_countdown(self):
        """Show countdown overlay before capturing"""
        self.countdown_window = tk.Toplevel(self.root)
        self.countdown_window.title("Koordinat Yakalama")
        self.countdown_window.geometry("300x150+500+300")
        self.countdown_window.attributes('-topmost', True)

        label = tk.Label(self.countdown_window,
                         text="Mouse'u istediğiniz pozisyona getirin\nKoordinat yakalaması başlıyor...",
                         font=('Arial', 12))
        label.pack(pady=20)

        self.countdown_label = tk.Label(self.countdown_window, text="3", font=('Arial', 48, 'bold'))
        self.countdown_label.pack()

        # Start countdown
        self.root.after(1000, lambda: self.countdown(3))

    def countdown(self, count):
        """Countdown timer"""
        if count > 0:
            self.countdown_label.config(text=str(count))
            self.root.after(1000, lambda: self.countdown(count - 1))
        else:
            # Capture coordinate
            self.capture_coordinate()

    def capture_coordinate(self):
        """Capture mouse position and save coordinate"""
        try:
            # Get current mouse position
            screen_x, screen_y = self.automation.get_mouse_position()

            # DEBUG: Print screen coordinates
            print(f"\n📍 Capturing '{self.capturing_coord_name}':")
            print(f"   Screen coordinates: ({screen_x}, {screen_y})")

            # Save as VM-relative coordinate
            self.coord_manager.save_coordinate(self.capturing_coord_name, screen_x, screen_y)

            # Get the VM-relative coordinates to display
            rel_x, rel_y = self.coord_manager.get_coordinate(self.capturing_coord_name)

            # DEBUG: Print relative coordinates
            print(f"   Saved as VM-relative: ({rel_x}, {rel_y})")

            # Update entry fields
            self.capturing_x_entry.delete(0, tk.END)
            self.capturing_x_entry.insert(0, str(rel_x))
            self.capturing_y_entry.delete(0, tk.END)
            self.capturing_y_entry.insert(0, str(rel_y))

            # Close countdown window
            if self.countdown_window:
                self.countdown_window.destroy()

            # Restore main window
            self.root.deiconify()

            # Show success message
            self.update_status(f"Koordinat '{self.capturing_coord_name}' kaydedildi: ({rel_x}, {rel_y})")

        except Exception as e:
            if self.countdown_window:
                self.countdown_window.destroy()
            self.root.deiconify()
            messagebox.showerror("Hata", f"Koordinat yakalama hatası: {e}")

    def debug_vmware_window(self):
        """Debug function to show VMware window detection info"""
        try:
            vm_window = self.coord_manager.get_vmware_window(debug=True)
            if vm_window:
                msg = f"✅ VMware Window Found:\n\n"
                msg += f"Title: {vm_window['title']}\n"
                msg += f"Owner: {vm_window['owner']}\n\n"
                msg += f"Position: ({vm_window['left']}, {vm_window['top']})\n"
                msg += f"Size: {vm_window['width']} x {vm_window['height']}\n\n"
                msg += f"Title Bar Height: {self.coord_manager.VMWARE_TOP_BORDER}px\n"
                msg += f"Content Area Starts at Y: {vm_window['top'] + self.coord_manager.VMWARE_TOP_BORDER}\n\n"
                msg += "Check console for detailed debug output."
                messagebox.showinfo("VMware Window Debug", msg)
            else:
                messagebox.showerror("Error", "VMware window not found!\nMake sure VMware Fusion is running.")
        except Exception as e:
            messagebox.showerror("Error", f"Debug error: {e}")

    def apply_and_show_overlay(self):
        """Apply offset settings and show overlay"""
        try:
            # Read values from UI
            offset_x = int(self.capture_offset_x.get())
            offset_y = int(self.capture_offset_y.get())
            width = int(self.capture_width.get())
            height = int(self.capture_height.get())

            # SYNC WITH OCR HANDLER
            self.ocr_handler.capture_offset_x = offset_x
            self.ocr_handler.capture_offset_y = offset_y
            self.ocr_handler.capture_width = width
            self.ocr_handler.capture_height = height

            print(f"\n✓ Yakalama bölgesi güncellendi: {width}x{height} at {offset_x},{offset_y}")

            # Show overlay with new settings
            self.show_capture_overlay()

        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayılar girin!")

    def show_capture_overlay(self):
        """Show visual overlay of capture region without saving"""
        print("\n=== Yakalama Bölgesi Overlay ===")
        print("Kırmızı overlay 2 saniye gösterilecek...")

        if not self.coord_manager.validate_coordinate('textbox'):
            messagebox.showerror("Hata", "Textbox koordinatı bulunamadı!")
            return

        textbox_coord = self.coord_manager.get_screen_coordinate('textbox')
        if textbox_coord:
            screen_x, screen_y = textbox_coord

            # Get offsets from OCR handler (user-adjustable)
            offset_x = getattr(self.ocr_handler, 'capture_offset_x', -100)
            offset_y = getattr(self.ocr_handler, 'capture_offset_y', -60)
            width = getattr(self.ocr_handler, 'capture_width', 200)
            height = getattr(self.ocr_handler, 'capture_height', 20)

            region_x = screen_x + offset_x
            region_y = screen_y + offset_y

            self.ocr_handler._show_capture_region_overlay(region_x, region_y, width, height)

            print(f"Overlay gösteriliyor:")
            print(f"  Position: ({region_x}, {region_y})")
            print(f"  Size: {width}x{height}")
            self.update_status("Yakalama bölgesi overlay gösterildi")

    def test_question_region(self):
        """Test capturing the question region and save as test image"""
        print("\n=== Soru Bölgesi Testi ===")
        print("Kırmızı overlay 2 saniye gösterilecek...")
        screenshot = self.ocr_handler.capture_question_region(
            save_path="test_question_region.png",
            show_overlay=True  # Show visual overlay
        )
        if screenshot:
            print("✓ Soru bölgesi yakalandı ve 'test_question_region.png' olarak kaydedildi")
            self.update_status("Soru bölgesi kaydedildi: test_question_region.png")
            messagebox.showinfo("Başarılı",
                              "Soru bölgesi yakalandı!\n\n"
                              "Dosya: test_question_region.png\n\n"
                              "Kırmızı overlay gösterildi - doğru bölgeyi yakalıyor mu?\n"
                              "Resmi kontrol edin!")
        else:
            print("✗ Soru bölgesi yakalanamadı")
            messagebox.showerror("Hata", "Soru bölgesi yakalanamadı - textbox koordinatını kontrol edin")

    def test_result_detection(self):
        """Test result message detection"""
        print("\n=== Sonuç Mesajı Testi ===")
        result = self.ocr_handler.check_result_message()

        if result == 'success':
            messagebox.showinfo("Test Sonucu", "✅ SUCCESS message detected!\n\nCheck console for details.")
        elif result == 'fail':
            messagebox.showinfo("Test Sonucu", "❌ FAIL message detected!\n\nCheck console for details.")
        elif result == 'unknown':
            messagebox.showwarning("Test Sonucu", "⚠ Unknown result message detected.\n\nCheck console and debug_comparisons/result_captured.png")
        elif result is None:
            messagebox.showinfo("Test Sonucu", "ℹ️ No result message detected.\n\nMake sure result region coordinates are set and a message is visible.")
        else:
            messagebox.showerror("Test Sonucu", f"Unexpected result: {result}")

    def quick_capture(self):
        """Quickly capture current question with auto-generated name"""
        print("\n=== HIZLI YAKALAMA ===")

        # Find next available number
        import os

        # Ensure directory exists
        if not os.path.exists(self.ocr_handler.questions_dir):
            os.makedirs(self.ocr_handler.questions_dir)

        # Generate the filename (capture_001, 002...)
        existing_files = os.listdir(self.ocr_handler.questions_dir)
        capture_nums = [int(f[8:-4]) for f in existing_files if f.startswith("capture_") and f.endswith(".png")]
        
        next_num = max(capture_nums) + 1 if capture_nums else 1
        template_name = f"capture_{next_num:03d}"

        # Call the updated handler
        if self.ocr_handler.save_current_question_template(template_name):
            self.update_status(f"✓ Kaydedildi: {template_name}.png")
            print(f"✅ Success: {template_name}.png")
        else:
            # Usually fails if Textbox coordinate is missing
            messagebox.showerror("Hata", "Yakalama başarısız! Textbox koordinatını kontrol edin.")

    def save_question_template(self):
        """Save current question region as a template"""
        template_name = self.template_name_entry.get().strip()
        if not template_name:
            messagebox.showerror("Hata", "Lütfen şablon adı girin")
            return

        print(f"\n=== Soru Şablonu Kaydediliyor: {template_name} ===")
        if self.ocr_handler.save_current_question_template(template_name):
            self.update_status(f"Şablon kaydedildi: {template_name}")
            messagebox.showinfo("Başarılı",
                              f"Soru şablonu kaydedildi!\n\n"
                              f"Şablon: {template_name}.png\n"
                              f"Klasör: questions/\n\n"
                              f"Şimdi ocr_handler.py dosyasında\n"
                              f"question_answers sözlüğüne cevabı ekleyin:\n\n"
                              f'"{template_name}": "CEVAP_BURAYA"')
            self.template_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Hata", "Şablon kaydedilemedi")
   

    def toggle_auto_save(self):
        """Enable/disable auto-save mode for unknown questions"""
        self.ocr_handler.auto_save_mode = self.auto_save_questions.get()
        status = "enabled" if self.ocr_handler.auto_save_mode else "disabled"
        print(f"✓ Auto-save {status}")
        self.update_status(f"Auto-save {status}")

    def toggle_automation(self):
        """Start or stop automation"""
        if self.automation.is_running:
            self.stop_automation()
        else:
            self.start_automation()

    def start_automation(self):
        """Start crafting automation"""
        self.automation.is_running = True
        self.start_button.config(bg='#dc3545', text='F8: STOP')  # Red when running
        self.update_status("Otomasyon başlatıldı...")

        # Run automation in separate thread
        thread = threading.Thread(target=self.run_crafting_sequence, daemon=True)
        thread.start()

    def stop_automation(self):
        """Stop automation"""
        self.automation.stop()
        self.start_button.config(bg='#28a745', text='F8: Start/Stop')  # Green when stopped
        self.update_status("Otomasyon durduruldu.")

    def run_crafting_sequence(self):
        """
        Main Loop: Supports Infinite Looping, Precise Timing, 
        and Math Skipping via check_and_handle_popup.
        """
        try:
            print("\n" + "="*60)
            print("  🚀 CRAFTING AUTOMATION STARTED (LOOP MODE)")
            print("="*60)

            # --- SETUP INITIAL STARTING CONDITIONS (First Run Only) ---
            is_first_run = True
            
            while self.automation.is_running:
                # 1. Get current settings from UI at the start of every cycle
                interval = int(self.craft_interval.get() or 30)
                d_key = self.d_key.get() or 'd'
                s_key = self.s_key.get() or 's'
                click_delay = int(self.click_delay.get() or 900) / 1000.0
                
                # Logic for skipping items/cycles only applies on the first run
                if is_first_run:
                    start_item_name = self.starting_item.get().lower().replace(" ", "_")
                    start_cycle_val = int(self.starting_cycle.get() or 1)
                    found_start_item = False 
                    print(f"▶️ Starting first run from: {start_item_name} (Item {start_cycle_val})")
                else:
                    start_item_name = "furboots" # Always restart from top
                    start_cycle_val = 1
                    found_start_item = True
                    print(f"\n🔄 Starting NEW cycle from the beginning...")

                last_popup_check = 0
                check_freq = 2.0 # Force a popup check every 2 seconds regardless

                items_to_craft = [
                    {'name': 'furboots', 'count': int(self.furboots_count.get() or 0)},
                    {'name': 'oil_cloth', 'count': int(self.oil_cloth_count.get() or 0)},
                    {'name': 'studded_gorget', 'count': int(self.studded_gorget_count.get() or 0)}
                ]

                # --- CRAFTING LOOP ---
                for item in items_to_craft:
                    if not self.automation.is_running: break
                    
                    # SKIP LOGIC: For the first run, skip until we hit the user's start item
                    if not found_start_item:
                        if item['name'] == start_item_name:
                            found_start_item = True
                        else:
                            print(f"⏭️ Skipping {item['name']}...")
                            continue

                    if item['count'] <= 0: continue

                    print(f"\n📦 Switching to {item['name'].upper()}...")
                    self.automation.click_at_coord(f"{item['name']}_group", triple_click=True)
                    time.sleep(1.0)

                    # Determine where to start inside this item count
                    actual_start = start_cycle_val if (is_first_run and item['name'] == start_item_name) else 1
                    
                    for i in range(actual_start, item['count'] + 1):
                        if not self.automation.is_running: break

                        # 1. Periodic Popup Check (Safety)
                        if time.time() - last_popup_check > check_freq:
                            if self.check_and_handle_popup(): 
                                last_popup_check = time.time()

                        # 2. Perform the Craft Click
                        self.automation.click_at_coord(f"{item['name']}_make")

                        # 3. PRECISE WAIT: Wait exactly 'click_delay' while checking for popups
                        # This prevents the "slowdown" caused by image processing time
                        start_time = time.time()
                        while (time.time() - start_time) < click_delay:
                            if not self.automation.is_running: break
                            
                            # Micro-check for popups during the wait
                            if self.ocr_handler.is_popup_visible():
                                if self.check_and_handle_popup():
                                    break # Exit the wait loop immediately if a popup was solved
                            time.sleep(0.05) # Small sleep to prevent high CPU usage

                        print(f"  ✓ {item['name']}: {i}/{item['count']}")

                        # 4. Maintenance (D/S or Makas) every 'interval' clicks
                        if i % interval == 0:
                            if item['name'] == 'oil_cloth':
                                self.automation.send_key(d_key); time.sleep(1)
                                if self.coord_manager.validate_coordinate('makas'):
                                    # Double-click on makas (scissors)
                                    self.automation.click_at_coord('makas', double_click=True)
                                    time.sleep(1)
                                    if self.coord_manager.validate_coordinate('kesilecek_item_oilcloth'):
                                        # Single-click on oil cloth to cut
                                        self.automation.click_at_coord('kesilecek_item_oilcloth')
                                        time.sleep(0.5)
                                        # Press ESC to unfocus
                                        self.automation.send_key('escape')
                                    time.sleep(1)
                            else:
                                self.automation.send_key(d_key); time.sleep(1)
                                self.automation.send_key(s_key); time.sleep(1)
                                if self.coord_manager.validate_coordinate('kesilecek_item'):
                                    self.automation.click_at_coord('kesilecek_item')
                                time.sleep(1)

                # --- END OF CRAFTING SEQUENCE ---
                if not self.automation.is_running: break

                # Final maintenance cleanup (Repeated twice as requested)
                for _ in range(2):
                    self.automation.send_key(d_key); time.sleep(1)
                    self.automation.send_key(s_key); time.sleep(1)
                    if self.coord_manager.validate_coordinate('kesilecek_item'):
                        self.automation.click_at_coord('kesilecek_item')
                    time.sleep(1)
                    pyautogui.press('esc'); time.sleep(0.5)

                # --- AMBAR (STORAGE) SEQUENCE ---
                if not self.automation.is_running: break
                k_key = self.k_key.get() or 'k'
                cloth_amt = self.cloth_amount.get() or '3500'
                leather_amt = self.leather_amount.get() or '838'

                print("\n📦 Opening Ambar...")
                self.automation.send_key(k_key); time.sleep(1.0)
                
                if self.coord_manager.validate_coordinate('kaynak_ekle'):
                    self.automation.click_at_coord('kaynak_ekle'); time.sleep(1)
                    for loc in ['ambar_loc1', 'ambar_loc2', 'ambar_loc3']:
                        if self.coord_manager.validate_coordinate(loc):
                            self.automation.click_at_coord(loc); time.sleep(1)
                    pyautogui.press('esc'); time.sleep(0.6)
                    self.automation.send_key(k_key); time.sleep(1.0)

                # Extract Resources
                for res_btn, amt in [('cloth_button', cloth_amt), ('leather_button', leather_amt)]:
                    if self.coord_manager.validate_coordinate(res_btn):
                        self.automation.click_at_coord(res_btn); time.sleep(0.8)
                        if self.coord_manager.validate_coordinate('istenilen_miktar'):
                            q_coord = self.coord_manager.get_screen_coordinate('istenilen_miktar')
                            pyautogui.click(q_coord[0], q_coord[1]); time.sleep(0.3)
                            for _ in range(5): pyautogui.press('backspace')
                            pyautogui.write(amt, interval=0.1); time.sleep(0.3)
                        if self.coord_manager.validate_coordinate('cantaya'):
                            self.automation.click_at_coord('cantaya'); time.sleep(0.8)

                # --- BOD COLLECTION ---
                if self.enable_bod_collection.get() and self.automation.is_running:
                    print("\n📋 Running BOD collection...")
                    self.run_bod_collection()

                # --- FINISH CYCLE ---
                is_first_run = False 
                print("\n✅ Cycle Finished. Restarting in 3 seconds...")
                time.sleep(3.0)

        except Exception as e:
            print(f"❌ Critical Error in crafting loop: {e}")
        finally:
            self.automation.reset()
            self.root.after(0, self.stop_automation)

    def run_bod_collection(self):
        """BOD Collection Automation - Runs after Ambar completes"""
        try:
            # Get current settings
            current_slot = int(self.coord_manager.settings.get('current_bod_slot', 1))
            page_offset = int(self.coord_manager.settings.get('page_offset', 0))
            f_key = self.f_key.get() or 'f'

            print(f"  Current BOD slot: {current_slot}, Page offset: {page_offset}")

            # Step 1: Close Ambar with right-click
            if self.coord_manager.validate_coordinate('close_ambar'):
                print("  🖱️ Right-clicking to close Ambar...")
                close_coord = self.coord_manager.get_screen_coordinate('close_ambar')
                pyautogui.rightClick(close_coord[0], close_coord[1])
                time.sleep(1.2)  # Increased delay
                # Check for popup after close
                if self.ocr_handler.is_popup_visible():
                    self.check_and_handle_popup()

            # Step 2: Press F key to open BOD dialog
            print(f"  ⌨️ Pressing {f_key} to open BOD dialog...")
            self.automation.send_key(f_key)
            time.sleep(1.5)  # Increased delay
            # Check for popup after F key
            if self.ocr_handler.is_popup_visible():
                self.check_and_handle_popup()

            # Step 3: Click Bod Hakları button to switch tab
            if self.coord_manager.validate_coordinate('bod_haklari_button'):
                print("  📑 Clicking Bod Hakları button...")
                self.automation.click_at_coord('bod_haklari_button')
                time.sleep(1.2)  # Increased delay
                # Check for popup after clicking button
                if self.ocr_handler.is_popup_visible():
                    self.check_and_handle_popup()

            # Step 4: Navigate to correct page (3 + page_offset clicks)
            sonraki_clicks = 3 + page_offset
            if self.coord_manager.validate_coordinate('sonraki_button'):
                print(f"  ➡️ Clicking Sonraki button {sonraki_clicks} times...")
                for _ in range(sonraki_clicks):
                    self.automation.click_at_coord('sonraki_button')
                    time.sleep(1.0)  # Increased delay
                    # Check for popup after each click
                    if self.ocr_handler.is_popup_visible():
                        self.check_and_handle_popup()

            # Step 5: Click the BOD slot
            slot_coord_name = f'bod_slot_{current_slot}'
            if self.coord_manager.validate_coordinate(slot_coord_name):
                print(f"  🎯 Selecting BOD slot {current_slot}...")
                self.automation.click_at_coord(slot_coord_name)
                time.sleep(1.2)  # Increased delay
                # Check for popup after slot selection
                if self.ocr_handler.is_popup_visible():
                    self.check_and_handle_popup()
            else:
                print(f"  ⚠️ BOD slot {current_slot} coordinate not set!")

            # Step 6: Close popup with right-click
            if self.coord_manager.validate_coordinate('popup_close'):
                print("  🖱️ Right-clicking to close popup...")
                popup_coord = self.coord_manager.get_screen_coordinate('popup_close')
                pyautogui.rightClick(popup_coord[0], popup_coord[1])
                time.sleep(1.0)  # Increased delay

            # Step 7: Increment slot tracking
            current_slot += 1
            if current_slot > 20:
                current_slot = 1
                page_offset += 1
                print(f"  🔄 Wrapped to slot 1, page offset now: {page_offset}")

            # Save updated values
            self.coord_manager.settings['current_bod_slot'] = current_slot
            self.coord_manager.settings['page_offset'] = page_offset
            self.coord_manager.save_config()

            # Update UI entry fields
            self.current_bod_slot_entry.delete(0, tk.END)
            self.current_bod_slot_entry.insert(0, str(current_slot))
            self.page_offset_entry.delete(0, tk.END)
            self.page_offset_entry.insert(0, str(page_offset))

            print(f"  ✅ BOD Collection complete! Next slot: {current_slot}")

        except Exception as e:
            print(f"  ❌ BOD Collection Error: {e}")

    def update_current_slot(self):
        """Update current BOD slot from UI entry"""
        try:
            new_slot = int(self.current_bod_slot_entry.get())
            if 1 <= new_slot <= 20:
                self.coord_manager.settings['current_bod_slot'] = new_slot
                self.coord_manager.save_config()
                messagebox.showinfo("Success", f"Current slot updated to {new_slot}")
                print(f"✓ Current BOD slot manually set to: {new_slot}")
            else:
                messagebox.showerror("Error", "Slot must be between 1 and 20")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def update_page_offset(self):
        """Update page offset from UI entry"""
        try:
            new_offset = int(self.page_offset_entry.get())
            if new_offset >= 0:
                self.coord_manager.settings['page_offset'] = new_offset
                self.coord_manager.save_config()
                messagebox.showinfo("Success", f"Page offset updated to {new_offset}")
                print(f"✓ Page offset manually set to: {new_offset}")
            else:
                messagebox.showerror("Error", "Page offset must be 0 or greater")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def handle_makro_kontrolu(self):
        """Returns True if answered, False if unknown, and 'SKIP' if math skipped"""
        answer = self.ocr_handler.find_question_match(confidence=0.75)
        
        if answer == "RETRY_MATH":
            txt_coord = self.coord_manager.get_screen_coordinate('textbox')
            if txt_coord:
                pyautogui.rightClick(txt_coord[0], txt_coord[1])
                time.sleep(0.5)
                m_key = self.m_key_entry.get() or 'm'
                pyautogui.press(m_key)
                # Wait for the old popup to clear and new one to start appearing
                time.sleep(2.0) 
                return "SKIP"
            return False

        if answer:
            txt = self.coord_manager.get_screen_coordinate('textbox')
            pyautogui.click(txt[0], txt[1], clicks=3)
            time.sleep(0.3)
            pyautogui.write(str(answer), interval=0.1)
            time.sleep(0.3)
            self.automation.click_at_coord('kontrol_et')
            time.sleep(1.0) # Wait for popup to disappear
            return True
            
        return False

    def check_and_handle_popup(self) -> bool:
        """Stays in a loop until the popup is either solved or skipped to a text question."""
        try:
            if self.ocr_handler.is_popup_visible():
                print("\n🔔 Popup Detected! Handling...")
                
                # We stay in this while loop as long as the popup is visible
                # This prevents the bot from returning to the crafting 'click' code
                while self.ocr_handler.is_popup_visible():
                    result = self.handle_makro_kontrolu()
                    
                    if result == "SKIP":
                        print("⏭️ Math skipped, waiting for next popup...")
                        time.sleep(1.0) # Pause to let the new window load
                        continue # Re-check the new popup in the next loop iteration
                    
                    if result is True:
                        print("✅ Popup solved.")
                        return True
                        
                    if result is False:
                        print("🛑 Unknown question. Stopping.")
                        self.stop_automation()
                        return False
            return False
        except Exception as e:
            print(f"Popup error: {e}")
            return False

    def load_coordinates_to_ui(self):
        """Load saved coordinates from config into UI fields"""
        try:
            coords = self.coord_manager.coordinates

            # Load craft coordinates
            if 'kesilecek_item' in coords:
                self.kesilecek_x.delete(0, tk.END)
                self.kesilecek_x.insert(0, str(coords['kesilecek_item']['x']))
                self.kesilecek_y.delete(0, tk.END)
                self.kesilecek_y.insert(0, str(coords['kesilecek_item']['y']))

            if 'kesilecek_item_oilcloth' in coords:
                self.kesilecek_oilcloth_x.delete(0, tk.END)
                self.kesilecek_oilcloth_x.insert(0, str(coords['kesilecek_item_oilcloth']['x']))
                self.kesilecek_oilcloth_y.delete(0, tk.END)
                self.kesilecek_oilcloth_y.insert(0, str(coords['kesilecek_item_oilcloth']['y']))

            # Load item group/make coordinates
            items = ['furboots', 'oil_cloth', 'studded_gorget']
            for item in items:
                if f'{item}_group' in coords:
                    gx_entry = getattr(self, f'{item}_gx')
                    gy_entry = getattr(self, f'{item}_gy')
                    gx_entry.delete(0, tk.END)
                    gx_entry.insert(0, str(coords[f'{item}_group']['x']))
                    gy_entry.delete(0, tk.END)
                    gy_entry.insert(0, str(coords[f'{item}_group']['y']))

                if f'{item}_make' in coords:
                    mx_entry = getattr(self, f'{item}_mx')
                    my_entry = getattr(self, f'{item}_my')
                    mx_entry.delete(0, tk.END)
                    mx_entry.insert(0, str(coords[f'{item}_make']['x']))
                    my_entry.delete(0, tk.END)
                    my_entry.insert(0, str(coords[f'{item}_make']['y']))

            # Load kontrol coordinates
            if 'textbox' in coords:
                self.textbox_x.delete(0, tk.END)
                self.textbox_x.insert(0, str(coords['textbox']['x']))
                self.textbox_y.delete(0, tk.END)
                self.textbox_y.insert(0, str(coords['textbox']['y']))

            if 'kontrol_et' in coords:
                self.kontrol_et_x.delete(0, tk.END)
                self.kontrol_et_x.insert(0, str(coords['kontrol_et']['x']))
                self.kontrol_et_y.delete(0, tk.END)
                self.kontrol_et_y.insert(0, str(coords['kontrol_et']['y']))

            if 'kapat' in coords:
                self.kapat_x.delete(0, tk.END)
                self.kapat_x.insert(0, str(coords['kapat']['x']))
                self.kapat_y.delete(0, tk.END)
                self.kapat_y.insert(0, str(coords['kapat']['y']))

            # Load Bitış tab coordinates
            if 'makas' in coords:
                self.makas_x.delete(0, tk.END)
                self.makas_x.insert(0, str(coords['makas']['x']))
                self.makas_y.delete(0, tk.END)
                self.makas_y.insert(0, str(coords['makas']['y']))

            if 'kaynak_ekle' in coords:
                self.kaynak_ekle_x.delete(0, tk.END)
                self.kaynak_ekle_x.insert(0, str(coords['kaynak_ekle']['x']))
                self.kaynak_ekle_y.delete(0, tk.END)
                self.kaynak_ekle_y.insert(0, str(coords['kaynak_ekle']['y']))

            if 'ambar_loc1' in coords:
                self.ambar_loc1_x.delete(0, tk.END)
                self.ambar_loc1_x.insert(0, str(coords['ambar_loc1']['x']))
                self.ambar_loc1_y.delete(0, tk.END)
                self.ambar_loc1_y.insert(0, str(coords['ambar_loc1']['y']))

            if 'ambar_loc2' in coords:
                self.ambar_loc2_x.delete(0, tk.END)
                self.ambar_loc2_x.insert(0, str(coords['ambar_loc2']['x']))
                self.ambar_loc2_y.delete(0, tk.END)
                self.ambar_loc2_y.insert(0, str(coords['ambar_loc2']['y']))

            if 'ambar_loc3' in coords:
                self.ambar_loc3_x.delete(0, tk.END)
                self.ambar_loc3_x.insert(0, str(coords['ambar_loc3']['x']))
                self.ambar_loc3_y.delete(0, tk.END)
                self.ambar_loc3_y.insert(0, str(coords['ambar_loc3']['y']))

            if 'cloth_button' in coords:
                self.cloth_button_x.delete(0, tk.END)
                self.cloth_button_x.insert(0, str(coords['cloth_button']['x']))
                self.cloth_button_y.delete(0, tk.END)
                self.cloth_button_y.insert(0, str(coords['cloth_button']['y']))

            if 'leather_button' in coords:
                self.leather_button_x.delete(0, tk.END)
                self.leather_button_x.insert(0, str(coords['leather_button']['x']))
                self.leather_button_y.delete(0, tk.END)
                self.leather_button_y.insert(0, str(coords['leather_button']['y']))

            if 'istenilen_miktar' in coords:
                self.istenilen_miktar_x.delete(0, tk.END)
                self.istenilen_miktar_x.insert(0, str(coords['istenilen_miktar']['x']))
                self.istenilen_miktar_y.delete(0, tk.END)
                self.istenilen_miktar_y.insert(0, str(coords['istenilen_miktar']['y']))

            if 'cantaya' in coords:
                self.cantaya_x.delete(0, tk.END)
                self.cantaya_x.insert(0, str(coords['cantaya']['x']))
                self.cantaya_y.delete(0, tk.END)
                self.cantaya_y.insert(0, str(coords['cantaya']['y']))

            # Load popup bounds coordinates
            if 'popup_top_left' in coords:
                self.popup_tl_x.delete(0, tk.END)
                self.popup_tl_x.insert(0, str(coords['popup_top_left']['x']))
                self.popup_tl_y.delete(0, tk.END)
                self.popup_tl_y.insert(0, str(coords['popup_top_left']['y']))

            if 'popup_bottom_right' in coords:
                self.popup_br_x.delete(0, tk.END)
                self.popup_br_x.insert(0, str(coords['popup_bottom_right']['x']))
                self.popup_br_y.delete(0, tk.END)
                self.popup_br_y.insert(0, str(coords['popup_bottom_right']['y']))

            # Load result region coordinates
            if 'result_top_left' in coords:
                self.result_tl_x.delete(0, tk.END)
                self.result_tl_x.insert(0, str(coords['result_top_left']['x']))
                self.result_tl_y.delete(0, tk.END)
                self.result_tl_y.insert(0, str(coords['result_top_left']['y']))

            if 'result_bottom_right' in coords:
                self.result_br_x.delete(0, tk.END)
                self.result_br_x.insert(0, str(coords['result_bottom_right']['x']))
                self.result_br_y.delete(0, tk.END)
                self.result_br_y.insert(0, str(coords['result_bottom_right']['y']))

            # Load M key setting (from settings, not coordinates)
            if 'm_key' in self.coord_manager.settings:
                self.m_key_entry.delete(0, tk.END)
                self.m_key_entry.insert(0, self.coord_manager.settings['m_key'])

            # Load click delay setting
            if 'click_delay' in self.coord_manager.settings:
                self.click_delay.delete(0, tk.END)
                self.click_delay.insert(0, self.coord_manager.settings['click_delay'])

            # Load Bitış tab settings
            if 'k_key' in self.coord_manager.settings:
                self.k_key.delete(0, tk.END)
                self.k_key.insert(0, self.coord_manager.settings['k_key'])

            if 'cloth_amount' in self.coord_manager.settings:
                self.cloth_amount.delete(0, tk.END)
                self.cloth_amount.insert(0, self.coord_manager.settings['cloth_amount'])

            if 'leather_amount' in self.coord_manager.settings:
                self.leather_amount.delete(0, tk.END)
                self.leather_amount.insert(0, self.coord_manager.settings['leather_amount'])

            # Load BOD tab coordinates
            if 'close_ambar' in coords:
                self.close_ambar_x.delete(0, tk.END)
                self.close_ambar_x.insert(0, str(coords['close_ambar']['x']))
                self.close_ambar_y.delete(0, tk.END)
                self.close_ambar_y.insert(0, str(coords['close_ambar']['y']))

            if 'bod_haklari_button' in coords:
                self.bod_haklari_x.delete(0, tk.END)
                self.bod_haklari_x.insert(0, str(coords['bod_haklari_button']['x']))
                self.bod_haklari_y.delete(0, tk.END)
                self.bod_haklari_y.insert(0, str(coords['bod_haklari_button']['y']))

            if 'sonraki_button' in coords:
                self.sonraki_button_x.delete(0, tk.END)
                self.sonraki_button_x.insert(0, str(coords['sonraki_button']['x']))
                self.sonraki_button_y.delete(0, tk.END)
                self.sonraki_button_y.insert(0, str(coords['sonraki_button']['y']))

            if 'popup_close' in coords:
                self.popup_close_x.delete(0, tk.END)
                self.popup_close_x.insert(0, str(coords['popup_close']['x']))
                self.popup_close_y.delete(0, tk.END)
                self.popup_close_y.insert(0, str(coords['popup_close']['y']))

            # Load 20 BOD slot coordinates
            for slot_num in range(1, 21):
                slot_name = f'bod_slot_{slot_num}'
                if slot_name in coords:
                    x_entry, y_entry = self.bod_slot_entries[slot_num]
                    x_entry.delete(0, tk.END)
                    x_entry.insert(0, str(coords[slot_name]['x']))
                    y_entry.delete(0, tk.END)
                    y_entry.insert(0, str(coords[slot_name]['y']))

            # Load BOD tab settings
            if 'f_key' in self.coord_manager.settings:
                self.f_key.delete(0, tk.END)
                self.f_key.insert(0, self.coord_manager.settings['f_key'])

            if 'start_bod_slot' in self.coord_manager.settings:
                self.start_bod_slot.delete(0, tk.END)
                self.start_bod_slot.insert(0, str(self.coord_manager.settings['start_bod_slot']))

            if 'enable_bod_collection' in self.coord_manager.settings:
                self.enable_bod_collection.set(self.coord_manager.settings['enable_bod_collection'])

            # Update current slot and page offset entry fields
            if 'current_bod_slot' in self.coord_manager.settings:
                self.current_bod_slot_entry.delete(0, tk.END)
                self.current_bod_slot_entry.insert(0, str(self.coord_manager.settings['current_bod_slot']))

            if 'page_offset' in self.coord_manager.settings:
                self.page_offset_entry.delete(0, tk.END)
                self.page_offset_entry.insert(0, str(self.coord_manager.settings['page_offset']))

            self.update_status("Kaydedilmiş koordinatlar yüklendi")

        except Exception as e:
            print(f"Koordinat yükleme hatası: {e}")

    def save_settings(self):
        """Save all settings to config"""
        try:
            # Update settings
            self.coord_manager.settings['starting_item'] = self.starting_item.get()
            self.coord_manager.settings['starting_cycle'] = int(self.starting_cycle.get())
            self.coord_manager.settings['image_search_tolerance'] = self.tolerance_var.get()

            # Save item counts
            self.coord_manager.settings['furboots_count'] = self.furboots_count.get()
            self.coord_manager.settings['oil_cloth_count'] = self.oil_cloth_count.get()
            self.coord_manager.settings['studded_gorget_count'] = self.studded_gorget_count.get()

            # Save M key setting
            self.coord_manager.settings['m_key'] = self.m_key_entry.get()

            # Save click delay setting
            self.coord_manager.settings['click_delay'] = self.click_delay.get()

            # Save Bitış tab settings
            self.coord_manager.settings['k_key'] = self.k_key.get()
            self.coord_manager.settings['cloth_amount'] = self.cloth_amount.get()
            self.coord_manager.settings['leather_amount'] = self.leather_amount.get()

            # Update hotkeys
            self.coord_manager.hotkeys['duzenle'] = self.duzenle_entry.get()
            self.coord_manager.hotkeys['kes'] = self.kes_entry.get()
            self.coord_manager.hotkeys['makrokliit'] = self.makrokliit_entry.get()

            # Save popup bounds coordinates (Entry fields contain VM-relative coords, save directly)
            if self.popup_tl_x.get() and self.popup_tl_y.get():
                self.coord_manager.coordinates['popup_top_left'] = {
                    'x': int(self.popup_tl_x.get()),
                    'y': int(self.popup_tl_y.get())
                }

            if self.popup_br_x.get() and self.popup_br_y.get():
                self.coord_manager.coordinates['popup_bottom_right'] = {
                    'x': int(self.popup_br_x.get()),
                    'y': int(self.popup_br_y.get())
                }

            # Save result region coordinates (Entry fields contain VM-relative coords, save directly)
            if self.result_tl_x.get() and self.result_tl_y.get():
                self.coord_manager.coordinates['result_top_left'] = {
                    'x': int(self.result_tl_x.get()),
                    'y': int(self.result_tl_y.get())
                }

            if self.result_br_x.get() and self.result_br_y.get():
                self.coord_manager.coordinates['result_bottom_right'] = {
                    'x': int(self.result_br_x.get()),
                    'y': int(self.result_br_y.get())
                }

            # Save BOD tab settings
            self.coord_manager.settings['f_key'] = self.f_key.get()
            self.coord_manager.settings['start_bod_slot'] = int(self.start_bod_slot.get() or 1)
            self.coord_manager.settings['enable_bod_collection'] = self.enable_bod_collection.get()

            # Initialize current_bod_slot and page_offset if not already set
            if 'current_bod_slot' not in self.coord_manager.settings:
                self.coord_manager.settings['current_bod_slot'] = int(self.start_bod_slot.get() or 1)
            if 'page_offset' not in self.coord_manager.settings:
                self.coord_manager.settings['page_offset'] = 0

            # Save BOD tab coordinates (Entry fields contain VM-relative coords, save directly)
            if self.close_ambar_x.get() and self.close_ambar_y.get():
                self.coord_manager.coordinates['close_ambar'] = {
                    'x': int(self.close_ambar_x.get()),
                    'y': int(self.close_ambar_y.get())
                }

            if self.bod_haklari_x.get() and self.bod_haklari_y.get():
                self.coord_manager.coordinates['bod_haklari_button'] = {
                    'x': int(self.bod_haklari_x.get()),
                    'y': int(self.bod_haklari_y.get())
                }

            if self.sonraki_button_x.get() and self.sonraki_button_y.get():
                self.coord_manager.coordinates['sonraki_button'] = {
                    'x': int(self.sonraki_button_x.get()),
                    'y': int(self.sonraki_button_y.get())
                }

            if self.popup_close_x.get() and self.popup_close_y.get():
                self.coord_manager.coordinates['popup_close'] = {
                    'x': int(self.popup_close_x.get()),
                    'y': int(self.popup_close_y.get())
                }

            # Save 20 BOD slot coordinates (Entry fields contain VM-relative coords, save directly)
            for slot_num in range(1, 21):
                x_entry, y_entry = self.bod_slot_entries[slot_num]
                if x_entry.get() and y_entry.get():
                    self.coord_manager.coordinates[f'bod_slot_{slot_num}'] = {
                        'x': int(x_entry.get()),
                        'y': int(y_entry.get())
                    }

            # Save to file
            self.coord_manager.save_config()

            self.update_status("Ayarlar kaydedildi!")
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")

    def update_vm_status(self):
        """Update VM window detection status and profile"""
        vm_window = self.coord_manager.get_vmware_window()
        if vm_window:
            self.vm_status_label.config(text=f"✓ VM Hazır: {vm_window['title']}", fg='green')
            # Update profile label with window title
            if vm_window['title']:
                self.profile_label.config(text=vm_window['title'])
            else:
                self.profile_label.config(text=f"VMware Fusion - {vm_window['owner']}")
        else:
            self.vm_status_label.config(text="✗ VM Bulunamadı - VMware Fusion'ı çalıştırın", fg='red')
            self.profile_label.config(text="VM bulunamadı", fg='red')

        # Check again after 5 seconds
        self.root.after(5000, self.update_vm_status)

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = UOCrafterApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
