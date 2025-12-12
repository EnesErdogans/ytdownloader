import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading


class YoutubeProjeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube İndirici - MP3 & MP4 (EnErd)")
        self.root.geometry("800x650")

        # Tema Ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'))

        # --- ÜST PANEL ---
        frame_top = tk.LabelFrame(root, text="İndirme Ayarları", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_top.pack(fill="x", padx=10, pady=5)

        # 1. Link Girişi
        tk.Label(frame_top, text="Video veya Playlist Linki:").grid(row=0, column=0, sticky="w")
        self.entry_url = tk.Entry(frame_top, width=60)
        self.entry_url.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # 2. Format Seçimi (MP3 / MP4)
        tk.Label(frame_top, text="Format Seçin:").grid(row=1, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP3 (Ses)")
        self.combo_format = ttk.Combobox(frame_top, textvariable=self.format_var, state="readonly", width=20)
        self.combo_format['values'] = ("MP3 (Ses)", "MP4 (Yüksek Kalite Video)")
        self.combo_format.grid(row=1, column=1, sticky="w", padx=5)

        # 3. Klasör Seçimi
        tk.Label(frame_top, text="Kaydedilecek Yer:").grid(row=2, column=0, sticky="w")
        frame_folder = tk.Frame(frame_top)
        frame_folder.grid(row=2, column=1, sticky="we", padx=5)

        self.entry_folder = tk.Entry(frame_folder, width=45)
        self.entry_folder.pack(side="left", fill="x", expand=True)

        btn_sel = tk.Button(frame_folder, text="Seç...", command=self.klasor_sec, width=10)
        btn_sel.pack(side="right", padx=5)

        self.varsayilan_klasor_ayarla()

        # Grid genişletme ayarı
        frame_top.columnconfigure(1, weight=1)

        # --- İŞLEM BUTONLARI ---
        frame_action = tk.Frame(root, pady=5)
        frame_action.pack(fill="x", padx=15)

        self.btn_baslat = tk.Button(frame_action, text="LİSTEYİ GETİR VE İNDİRMEYİ BAŞLAT",
                                    bg="#2E7D32", fg="white", font=("Arial", 11, "bold"), height=2,
                                    command=self.baslat_thread)
        self.btn_baslat.pack(fill="x")

        # İlerleme Çubuğu
        self.progress = ttk.Progressbar(frame_action, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=10)

        self.lbl_status = tk.Label(frame_action, text="Hazır", font=("Arial", 10))
        self.lbl_status.pack()

        # --- LİSTE GÖRÜNÜMÜ (TREEVIEW) ---
        frame_list = tk.LabelFrame(root, text="İndirme Kuyruğu", padx=5, pady=5)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("sira", "ad", "durum")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings")

        self.tree.heading("sira", text="No")
        self.tree.heading("ad", text="Video Başlığı")
        self.tree.heading("durum", text="Durum")

        self.tree.column("sira", width=50, anchor="center")
        self.tree.column("ad", width=500, anchor="w")
        self.tree.column("durum", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Renk Etiketleri
        self.tree.tag_configure('ok', background='#C8E6C9')  # Yeşil
        self.tree.tag_configure('wait', background='#FFF9C4')  # Sarı
        self.tree.tag_configure('err', background='#FFCDD2')  # Kırmızı
        self.tree.tag_configure('active', background='#BBDEFB')  # Mavi

    def varsayilan_klasor_ayarla(self):
        # D sürücüsü varsa D, yoksa Masaüstü
        if os.path.exists("D:/"):
            path = "D:/Youtube_Downloads"
        else:
            path = os.path.join(os.path.expanduser("~"), "Desktop", "Youtube_Downloads")
        self.entry_folder.insert(0, path)

    def klasor_sec(self):
        d = filedialog.askdirectory()
        if d:
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, d)

    def baslat_thread(self):
        url = self.entry_url.get()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen bir link girin!")
            return

        self.btn_baslat.config(state="disabled", text="İşlem Sürüyor...")
        self.tree.delete(*self.tree.get_children())  # Listeyi temizle

        # İşlemi ayrı thread'de başlat
        threading.Thread(target=self.ana_islem, args=(url,), daemon=True).start()

    def ana_islem(self, url):
        target_folder = self.entry_folder.get()
        secilen_format = self.format_var.get()  # MP3 mü MP4 mü?

        try:
            self.lbl_status.config(text="Bilgiler çekiliyor, lütfen bekleyin...")

            # --- ADIM 1: Video Listesini Çek ---
            ydl_opts_info = {
                'extract_flat': True,  # Hızlı çekim modu
                'quiet': True,
                'ignoreerrors': True
            }

            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)

                # Playlist mi yoksa tek video mu?
                if 'entries' in info:
                    playlist_title = info.get('title', 'Playlist')
                    # Playlist için alt klasör oluştur
                    save_path = os.path.join(target_folder, playlist_title)
                    entries = list(info['entries'])
                else:
                    save_path = target_folder
                    entries = [info]

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Listeyi GUI'ye doldur
            download_queue = []
            for i, entry in enumerate(entries, 1):
                if entry is None: continue  # Silinmiş video koruması

                title = entry.get('title', 'Bilinmeyen Video')
                video_id = entry.get('id')
                # En sağlam link oluşturma yöntemi:
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                item_id = self.tree.insert("", "end", values=(i, title, "Bekliyor"), tags=('wait',))
                download_queue.append((item_id, video_url, title))

            # Progress Bar ayarla
            self.progress["maximum"] = len(download_queue)
            self.progress["value"] = 0

            # --- ADIM 2: İndirme Döngüsü ---
            for i, (item_id, v_url, v_title) in enumerate(download_queue, 1):
                self.lbl_status.config(text=f"İndiriliyor ({i}/{len(download_queue)}): {v_title}")
                self.tree.item(item_id, values=(i, v_title, "İndiriliyor..."), tags=('active',))
                self.tree.see(item_id)

                try:
                    self.indir_tekli(v_url, save_path, secilen_format)
                    # Başarılı
                    self.tree.item(item_id, values=(i, v_title, "Tamamlandı"), tags=('ok',))
                except Exception as e:
                    # Hata
                    err_msg = str(e).split('\n')[0]  # Hatayı kısalt
                    if "ffmpeg" in err_msg.lower():
                        err_msg = "FFmpeg Eksik!"
                    self.tree.item(item_id, values=(i, v_title, err_msg), tags=('err',))
                    print(f"Hata detayı: {e}")

                self.progress["value"] = i

            self.lbl_status.config(text="Tüm işlemler bitti!")
            messagebox.showinfo("Başarılı", f"İndirme tamamlandı!\nKlasör: {save_path}")

        except Exception as e:
            messagebox.showerror("Kritik Hata", f"Listeyi çekerken hata oluştu:\n{e}")
        finally:
            self.btn_baslat.config(state="normal", text="LİSTEYİ GETİR VE İNDİRMEYİ BAŞLAT")

    def indir_tekli(self, url, folder, format_type):
        """Format seçimine göre indirme yapan fonksiyon"""

        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        if "MP3" in format_type:
            # MP3 AYARLARI
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # MP4 AYARLARI
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                # Video ve sesi birleştirmek için yine ffmpeg gerekebilir
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


if __name__ == "__main__":
    # FFmpeg kontrolü (Basit uyarı)
    try:
        import shutil

        if shutil.which("ffmpeg") is None:
            print("UYARI: FFmpeg sistemde bulunamadı. MP3 dönüştürme çalışmayabilir.")
    except:
        pass

    root = tk.Tk()
    app = YoutubeProjeApp(root)
    root.mainloop()
