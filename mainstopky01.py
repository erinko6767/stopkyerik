import tkinter as tk
import time

# --- Farebná paleta (Godmode Cyber HUD) ---
PALETA = {
    "bg_hlavne": "#070b14",
    "bg_karta": "#0e1626",
    "bg_karta_2": "#131f36",
    "okraj_neon": "#00f0ff",
    "okraj_fialova": "#a855f7",
    "okraj_zelena": "#10b981",
    "okraj_cervena": "#ef4444",
    "text_hlavny": "#f8fafc",
    "text_tlmeny": "#7dd3fc",
    "text_sedy": "#64748b",
    "cas_bezi": "#00f5d4",
    "cas_pauza": "#fbbf24",
    "cas_nula": "#38bdf8",
}

# Globálne premenné stavu stopiek
bezi = False
zaciatok_casu = 0.0
uplynuly_cas = 0.0
kola = []
posledny_cas_kola = 0.0
pulz_faza = 0.0


def formatuj_cas(sekundy):
    """Formátuje sekundy do tvaru MM:SS.stotiny."""
    sekundy = max(0.0, sekundy)
    minuty = int(sekundy // 60)
    zvysok_sekund = int(sekundy % 60)
    stotiny = int((sekundy - int(sekundy)) * 100)
    return f"{minuty:02d}:{zvysok_sekund:02d}.{stotiny:02d}"


def vykresli_zaobleny_panel(canvas, x1, y1, x2, y2, r=14, fill="#0e1626", outline="#00f0ff", sirka=2, tag="panel"):
    """Vykreslí zaoblený obdĺžnik na Canvas bez externých knižníc."""
    body = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(body, smooth=True, fill=fill, outline=outline, width=sirka, tags=tag)


def vykresli_hud_tlacidlo(canvas, text, akcia, farba_akcentu, sirka=122, vysoky=42):
    """Vytvorí vlastné animované neonové tlačidlo na Canvas."""
    c = tk.Canvas(
        canvas,
        width=sirka,
        height=vysoky,
        bg=PALETA["bg_karta"],
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )
    vykresli_zaobleny_panel(
        c, 3, 3, sirka - 3, vysoky - 3,
        r=10, fill=PALETA["bg_karta_2"], outline=farba_akcentu, sirka=2, tag="btn_bg"
    )
    c.create_text(
        sirka // 2, vysoky // 2,
        text=text,
        fill=PALETA["text_hlavny"],
        font=("Consolas", 10, "bold"),
        tags="btn_text"
    )

    def pri_vstupe(_event):
        c.delete("btn_bg")
        vykresli_zaobleny_panel(
            c, 2, 2, sirka - 2, vysoky - 2,
            r=10, fill=farba_akcentu, outline=PALETA["text_hlavny"], sirka=2, tag="btn_bg"
        )
        c.itemconfig("btn_text", fill="#050811")
        c.tag_raise("btn_text")

    def pri_odchode(_event):
        c.delete("btn_bg")
        vykresli_zaobleny_panel(
            c, 3, 3, sirka - 3, vysoky - 3,
            r=10, fill=PALETA["bg_karta_2"], outline=farba_akcentu, sirka=2, tag="btn_bg"
        )
        c.itemconfig("btn_text", fill=PALETA["text_hlavny"])
        c.tag_raise("btn_text")

    def pri_kliku(_event):
        akcia()

    c.bind("<Enter>", pri_vstupe)
    c.bind("<Leave>", pri_odchode)
    c.bind("<Button-1>", pri_kliku)
    c.akcia_callback = akcia
    c.farba_akcentu = farba_akcentu
    return c


def nastav_text_hud_tlacidla(c, novy_text):
    """Aktualizuje text vo vlastnom Canvas tlačidle."""
    c.itemconfig("btn_text", text=novy_text)


# 1. CALLBACK FUNKCIA: Reaguje na časovač (.after) a plynule aktualizuje čas, indikátor a animáciu HUD
def aktualizuj_cas():
    global uplynuly_cas, pulz_faza
    if bezi:
        uplynuly_cas = time.time() - zaciatok_casu
        label_cas.config(text=formatuj_cas(uplynuly_cas), fg=PALETA["cas_bezi"])

        # Pulzujúci stavový LED indikátor
        pulz_faza += 0.35
        radius = 6 + int(2.5 * (0.5 + 0.5 * __import__("math").sin(pulz_faza)))
        canvas_status.delete("led")
        canvas_status.create_oval(
            14 - radius, 14 - radius, 14 + radius, 14 + radius,
            fill=PALETA["okraj_zelena"], outline="#a7f3d0", width=2, tags="led"
        )
        okno.after(20, aktualizuj_cas)


# 2. CALLBACK FUNKCIA: Reaguje na tlačidlo Štart/Stop alebo stlačenie Medzerníka
def prepni_start_stop(event=None):
    global bezi, zaciatok_casu
    if not bezi:
        bezi = True
        zaciatok_casu = time.time() - uplynuly_cas
        label_stav.config(text="STATUS // RUNNING", fg=PALETA["okraj_zelena"])
        nastav_text_hud_tlacidla(btn_start_stop, "PAUSE [SPACE]")
        canvas_status.delete("led")
        canvas_status.create_oval(7, 7, 21, 21, fill=PALETA["okraj_zelena"], outline="#a7f3d0", width=2, tags="led")
        aktualizuj_cas()
    else:
        bezi = False
        label_stav.config(text="STATUS // PAUSED", fg=PALETA["cas_pauza"])
        label_cas.config(fg=PALETA["cas_pauza"])
        nastav_text_hud_tlacidla(btn_start_stop, "RESUME [SPACE]")
        canvas_status.delete("led")
        canvas_status.create_oval(8, 8, 20, 20, fill=PALETA["cas_pauza"], outline="#fef08a", width=2, tags="led")


# 3. CALLBACK FUNKCIA: Reaguje na tlačidlo Reset alebo stlačenie klávesu R
def resetuj_stopky(event=None):
    global bezi, uplynuly_cas, kola, posledny_cas_kola
    bezi = False
    uplynuly_cas = 0.0
    posledny_cas_kola = 0.0
    kola.clear()
    label_cas.config(text="00:00.00", fg=PALETA["cas_nula"])
    label_stav.config(text="STATUS // RESET COMPLETE", fg=PALETA["text_tlmeny"])
    nastav_text_hud_tlacidla(btn_start_stop, "START [SPACE]")
    listbox_kola.delete(0, tk.END)
    canvas_status.delete("led")
    canvas_status.create_oval(8, 8, 20, 20, fill=PALETA["okraj_neon"], outline="#bae6fd", width=2, tags="led")


# 4. CALLBACK FUNKCIA: Reaguje na tlačidlo Kolo alebo stlačenie klávesu L
def zapis_kolo(event=None):
    global posledny_cas_kola
    if uplynuly_cas > 0:
        cislo_kola = len(kola) + 1
        celkovy_str = formatuj_cas(uplynuly_cas)
        rozdiel = uplynuly_cas - posledny_cas_kola
        rozdiel_str = formatuj_cas(rozdiel)
        posledny_cas_kola = uplynuly_cas

        zaznam = f"#{cislo_kola:02d}   {celkovy_str}   (+{rozdiel_str})"
        kola.append(zaznam)
        listbox_kola.insert(tk.END, zaznam)
        listbox_kola.see(tk.END)
        label_stav.config(text=f"LAP #{cislo_kola:02d} LOGGED // {celkovy_str}", fg=PALETA["okraj_fialova"])


# 5. CALLBACK FUNKCIA: Reaguje na stlačenie klávesy cez bind na klávesnicu a využíva event.keysym
def obsluha_klavesnice(event):
    klaves = event.keysym.lower()
    if klaves == "space":
        prepni_start_stop()
    elif klaves == "r":
        resetuj_stopky()
    elif klaves == "l":
        zapis_kolo()


# 6. CALLBACK FUNKCIA: Reaguje na kliknutie myšou na displej cez bind a využíva event.x, event.y
def klik_na_displej(event):
    label_stav.config(
        text=f"CLICK [x={event.x}, y={event.y}] -> TOGGLE TIMER",
        fg=PALETA["okraj_neon"]
    )
    prepni_start_stop()


# 7. CALLBACK FUNKCIA (cez lambda s parametrom): Mení farebný akcent HUD rámu a okrajov
def zmen_neon_motív(farba_hlavna, farba_sekundarna, nazov_motivu):
    okno.config(bg=farba_hlavna)
    for frame in (frame_hlavicka, frame_displej, frame_tlacidla, frame_motivy, frame_kola):
        frame.config(bg=farba_hlavna)

    label_nadpis.config(bg=farba_hlavna, fg=farba_sekundarna)
    label_navod.config(bg=farba_hlavna, fg=PALETA["text_tlmeny"])
    label_stav.config(bg=farba_hlavna)
    label_motivy_titulok.config(bg=farba_hlavna, fg=PALETA["text_sedy"])
    label_kola_hlavicka.config(bg=farba_hlavna, fg=farba_sekundarna)
    canvas_status.config(bg=farba_hlavna)
    label_cas.config(highlightbackground=farba_sekundarna)
    listbox_kola.config(highlightbackground=farba_sekundarna)
    label_stav.config(text=f"THEME // {nazov_motivu}", fg=farba_sekundarna)


# --- Hlavné okno ---
okno = tk.Tk()
okno.title("CHRONO // GODMODE HUD — Téma 8: Stopky")
okno.geometry("500x610")
okno.resizable(False, False)
okno.config(bg=PALETA["bg_hlavne"])

# Hlavička a návod
frame_hlavicka = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_hlavicka.pack(fill="x", padx=24, pady=(16, 6))

label_nadpis = tk.Label(
    frame_hlavicka,
    text="CHRONO // GODMODE STOPWATCH",
    font=("Consolas", 16, "bold"),
    bg=PALETA["bg_hlavne"],
    fg=PALETA["okraj_neon"]
)
label_nadpis.pack(anchor="w")

label_navod = tk.Label(
    frame_hlavicka,
    text="[SPACE] Štart/Stop   [R] Reset   [L] Kolo   •   Klik na displej = Štart/Stop",
    font=("Consolas", 9),
    bg=PALETA["bg_hlavne"],
    fg=PALETA["text_tlmeny"]
)
label_navod.pack(anchor="w", pady=(2, 0))

# Hlavný digitálny displej
frame_displej = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_displej.pack(fill="x", padx=24, pady=8)

label_cas = tk.Label(
    frame_displej,
    text="00:00.00",
    font=("Consolas", 44, "bold"),
    bg=PALETA["bg_karta"],
    fg=PALETA["cas_nula"],
    padx=20,
    pady=14,
    highlightthickness=2,
    highlightbackground=PALETA["okraj_neon"],
    cursor="hand2"
)
label_cas.pack(fill="x")

# Stavový riadok s LED indikátorom
frame_stav = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_stav.pack(fill="x", padx=24, pady=(2, 8))

canvas_status = tk.Canvas(
    frame_stav,
    width=28,
    height=28,
    bg=PALETA["bg_hlavne"],
    highlightthickness=0,
    bd=0
)
canvas_status.pack(side="left")
canvas_status.create_oval(8, 8, 20, 20, fill=PALETA["okraj_neon"], outline="#bae6fd", width=2, tags="led")

label_stav = tk.Label(
    frame_stav,
    text="STATUS // READY",
    font=("Consolas", 10, "bold"),
    bg=PALETA["bg_hlavne"],
    fg=PALETA["text_tlmeny"]
)
label_stav.pack(side="left", padx=8)

# Vlastné Canvas tlačidlá (command= cez pomocné volanie bez zátvoriek)
frame_tlacidla = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_tlacidla.pack(pady=6)

btn_start_stop = vykresli_hud_tlacidlo(
    frame_tlacidla, "START [SPACE]", prepni_start_stop, PALETA["okraj_zelena"], sirka=146, vysoky=44
)
btn_start_stop.grid(row=0, column=0, padx=6)

btn_kolo = vykresli_hud_tlacidlo(
    frame_tlacidla, "LAP [L]", zapis_kolo, PALETA["okraj_fialova"], sirka=136, vysoky=44
)
btn_kolo.grid(row=0, column=1, padx=6)

btn_reset = vykresli_hud_tlacidlo(
    frame_tlacidla, "RESET [R]", resetuj_stopky, PALETA["okraj_cervena"], sirka=136, vysoky=44
)
btn_reset.grid(row=0, column=2, padx=6)

# Prepínače motívu cez callback s parametrom (lambda)
frame_motivy = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_motivy.pack(pady=(10, 4))

label_motivy_titulok = tk.Label(
    frame_motivy,
    text="HUD SKIN:",
    font=("Consolas", 9, "bold"),
    bg=PALETA["bg_hlavne"],
    fg=PALETA["text_sedy"]
)
label_motivy_titulok.pack(side="left", padx=(0, 8))

tk.Button(
    frame_motivy,
    text="CYBER CYAN",
    font=("Consolas", 8, "bold"),
    bg=PALETA["bg_karta_2"],
    fg=PALETA["okraj_neon"],
    activebackground=PALETA["okraj_neon"],
    activeforeground="#050811",
    relief="flat",
    padx=10,
    pady=4,
    cursor="hand2",
    command=lambda: zmen_neon_motív("#070b14", "#00f0ff", "CYBER CYAN")
).pack(side="left", padx=4)

tk.Button(
    frame_motivy,
    text="HYPER VIOLET",
    font=("Consolas", 8, "bold"),
    bg=PALETA["bg_karta_2"],
    fg=PALETA["okraj_fialova"],
    activebackground=PALETA["okraj_fialova"],
    activeforeground="#050811",
    relief="flat",
    padx=10,
    pady=4,
    cursor="hand2",
    command=lambda: zmen_neon_motív("#0c0716", "#c084fc", "HYPER VIOLET")
).pack(side="left", padx=4)

# Zoznam kôl (celkový čas + dĺžka kola)
frame_kola = tk.Frame(okno, bg=PALETA["bg_hlavne"])
frame_kola.pack(fill="both", expand=True, padx=24, pady=(8, 18))

label_kola_hlavicka = tk.Label(
    frame_kola,
    text="LAP TELEMETRY   (KOLO   CELKOM     DĹŽKA KOLA)",
    font=("Consolas", 9, "bold"),
    bg=PALETA["bg_hlavne"],
    fg=PALETA["okraj_neon"],
    anchor="w"
)
label_kola_hlavicka.pack(fill="x", pady=(0, 4))

listbox_kola = tk.Listbox(
    frame_kola,
    font=("Consolas", 11, "bold"),
    bg=PALETA["bg_karta"],
    fg=PALETA["text_hlavny"],
    selectbackground=PALETA["okraj_fialova"],
    selectforeground="#ffffff",
    highlightthickness=2,
    highlightbackground=PALETA["okraj_neon"],
    relief="flat",
    bd=6,
    height=7
)
listbox_kola.pack(fill="both", expand=True)

# --- Udalosti cez bind (klávesnica aj myš) ---
okno.bind("<KeyPress>", obsluha_klavesnice)
label_cas.bind("<Button-1>", klik_na_displej)

okno.mainloop()