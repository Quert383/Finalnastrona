import streamlit as st
import time
import base64
from scipy.optimize import newton

# Konfiguracja strony
st.set_page_config(
    page_title="Kalkulator MPKK | Salutaris Polska",
    page_icon="Salutaris_logo.png",
    layout="centered"
)

# Logo i nagłówek
with open("Salutaris_logo.png", "rb") as f:
    logo_data = f.read()
encoded_logo = base64.b64encode(logo_data).decode()

st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{encoded_logo}' style='width:300px;' />
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<h1 style='margin-bottom:0.2em;'>Kwalifikacja do SKD wraz z kalkulatorem MPKK</h1>"
    "<div style='color:#333; font-size:1.1rem; margin-bottom:1em;'>"
    "Sprawdź czy Twój kredyt się kwalifikuje oraz oblicz maksymalne pozaodsetkowe koszty kredytu konsumenckiego według aktualnych przepisów."
    "</div>",
    unsafe_allow_html=True
)
st.divider()

# --- 1. Termin zawarcia umowy ---
st.header("Wybierz termin zawarcia umowy kredytu", divider="gray")
terminy = [
    "11.03.2016 - 30.03.2020",
    "31.03.2020 - 30.06.2021",
    "01.07.2021 - 17.12.2022",
    "Od 18.12.2022"
]
choice_idx = st.radio(
    label="",
    options=list(range(len(terminy))),
    format_func=lambda i: terminy[i],
    index=0,
    key="termin"
)
choice = str(choice_idx + 1)

# Informacja o starszych umowach
st.warning(
    "Jeśli umowa została zawarta **przed 11 marca 2016 roku**, "
    "ale **po 18 grudnia 2011 roku**, "
    "możliwe jest zastosowanie SKD. Skontaktuj się z nami w celu indywidualnej analizy."
)
st.divider()

# --- 2. Rodzaj kredytu ---
st.header("Wybierz rodzaj kredytu", divider="gray")

rodzaje_kredytu_all = [
    "🧾 Kredyt konsumencki",
    "💸 Umowa pożyczki",
    "💳 Kredyt odnawialny",
    "🏦 Kredyt w rozumieniu prawa bankowego",
    "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości",
    "🤝 Kredyt polegający na zaciągnięciu zobowiązania wobec osoby trzeciej z obowiązkiem zwrotu kredytodawcy określonego świadczenia",
    "⏳ Umowa o odroczeniu terminu spełnienia świadczenia pieniężnego",
    "🏡 Kredyt hipoteczny",
    "🚗 Leasing bez obowiązku nabycia przedmiotu przez konsumenta",
]

rodzaje_kredytu = rodzaje_kredytu_all.copy()
if choice == "1":
    rodzaje_kredytu = [r for r in rodzaje_kredytu if r != "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości"]

kredyt = st.selectbox(
    label="Rodzaj kredytu:",
    options=rodzaje_kredytu,
    key="rodzaj"
)

if kredyt in ["🏡 Kredyt hipoteczny", "🚗 Leasing bez obowiązku nabycia przedmiotu przez konsumenta"]:
    st.warning(
        "**Twoja sprawa może wymagać indywidualnej analizy.** "
        "Wybrany rodzaj kredytu nie kwalifikuje się do standardowego wyliczenia MPKK. "
        "Skontaktuj się z prawnikiem lub doradcą finansowym."
    )
    st.stop()

# --- Weryfikacja wymogów formalnych i szczegółowych ---
st.header("Weryfikacja wymogów umowy", divider="gray")
naruszenia = []

wszystkie_pytania = [
    ("Czy umowa została zawarta w formie pisemnej?", "Umowa nie została zawarta w formie pisemnej (art. 29 ust. 1 u.k.k.)"),
    ("Czy w umowie zawarto Twoje imię, nazwisko i adres jako konsumenta oraz imię, nazwisko (nazwę) i adres (siedzibę) oraz adres do doręczeń elektronicznych kredytodawcy i pośrednika kredytowego?", "Brak pełnych danych identyfikujących strony umowy (art. 30 ust. 1 pkt 1 u.k.k.)"),
    ("Czy w umowie zawarto pouczenie o art. 37 ustawy o kredycie konsumenckim (uprawnienie do żądania bezpłatnego harmonogramu spłat)?", "Brak pouczenia o prawie do harmonogramu spłat (art. 30 ust. 1 pkt 8 u.k.k.)"),
    ("Czy umowa zawiera nazwany rodzaj kredytu?", "Brak nazwanego rodzaju kredytu (art. 30 ust. 1 pkt 2 u.k.k.)"),
    ("Czy umowa zawiera czas obowiązywania umowy?", "Brak określenia czasu obowiązywania umowy (art. 30 ust. 1 pkt 3 u.k.k.)"),
    ("Czy umowa zawiera całkowitą kwotę kredytu?", "Brak całkowitej kwoty kredytu (art. 30 ust. 1 pkt 4 u.k.k.)"),
    ("Czy umowa zawiera terminy i sposób wypłaty kredytu?", "Brak terminów i sposobu wypłaty (art. 30 ust. 1 pkt 5 u.k.k.)"),
    ("Czy umowa zawiera wskazaną stopę oprocentowania kredytu, warunki stosowania tej stopy, a także okresy, warunki i procedury zmiany stopy oprocentowania wraz z podaniem indeksu lub stopy referencyjnej (jeśli dotyczy)?", "Brak pełnych informacji o stopie oprocentowania (art. 30 ust. 1 pkt 6 u.k.k.)"),
    ("Czy umowa zawiera informację o innych kosztach, które konsument jest zobowiązany ponieść w związku z umową (opłaty, prowizje, marże, koszty usług dodatkowych, warunki zmiany kosztów)?", "Brak informacji o dodatkowych kosztach (art. 30 ust. 1 pkt 10 u.k.k.)"),
    ("Czy umowa zawiera informację o rocznej stopie oprocentowania zadłużenia przeterminowanego, warunki jej zmiany oraz ewentualne inne opłaty z tytułu zaległości w spłacie kredytu?", "Brak informacji o konsekwencjach przeterminowania (art. 30 ust. 1 pkt 13 u.k.k.)"),
    ("Czy umowa zawiera wskazany sposób zabezpieczenia i ubezpieczenia spłaty kredytu, jeżeli umowa je przewiduje?", "Brak informacji o zabezpieczeniach (art. 30 ust. 1 pkt 15 u.k.k.)"),
    ("Czy umowa zawiera termin, sposób i skutki odstąpienia konsumenta od umowy, obowiązek zwrotu przez konsumenta udostępnionego kredytu oraz odsetek, a także kwotę odsetek należnych w stosunku dziennym?", "Brak informacji o odstąpieniu od umowy (art. 30 ust. 1 pkt 17 u.k.k.)"),
    ("Czy umowa zawiera pouczenie o prawie konsumenta do spłaty kredytu przed terminem oraz procedurę spłaty kredytu przed terminem?", "Brak informacji o wcześniejszej spłacie (art. 30 ust. 1 pkt 18 u.k.k.)"),
    ("Czy umowa zawiera informację o prawie kredytodawcy do otrzymania prowizji za spłatę kredytu przed terminem i o sposobie jej ustalania, o ile takie prawo zastrzeżono w umowie?", "Brak informacji o prowizji za wcześniejszą spłatę (art. 30 ust. 1 pkt 19 u.k.k.)"),
    ("Czy w umowie naliczono odsetki i opłaty za opóźnienie?", "Brak klauzuli o odsetkach za opóźnienie (art. 30 ust. 1 pkt 13 u.k.k.)")
]

for idx, (pytanie, komunikat) in enumerate(wszystkie_pytania, 1):
    odpowiedz = st.radio(
        f"{idx}. {pytanie}",
        ["Tak", "Nie"],
        key=f"pytanie_{idx}"
    )
    if odpowiedz == "Nie":
        naruszenia.append(komunikat)
        st.warning("⚠️ Potencjalne naruszenie wymogów formalnych")

# --- Kredyt wiązany: pytania warunkowe ---
st.header("Kredyt wiązany – dodatkowe wymogi", divider="gray")
kredyt_wiazany_odp = st.radio(
    "Czy umowa to umowa o kredyt wiązany?",
    ["Nie", "Tak"],
    key="kredyt_wiazany"
)
if kredyt_wiazany_odp == "Tak":
    opis_towaru = st.radio(
        "1. Czy umowa zawiera opis towaru lub usługi?",
        ["Tak", "Nie"],
        key="opis_towaru"
    )
    if opis_towaru == "Nie":
        naruszenia.append("W Twojej umowie o kredyt wiązany nie zawarto opisu towaru lub usługi.")
        st.warning("⚠️ Brak opisu towaru lub usługi może skutkować zastosowaniem SKD.")

    cena_towaru = st.radio(
        "2. Czy umowa zawiera cenę nabycia towaru lub usługi?",
        ["Tak", "Nie"],
        key="cena_towaru"
    )
    if cena_towaru == "Nie":
        naruszenia.append("W Twojej umowie o kredyt wiązany nie zawarto ceny nabycia towaru lub usługi.")
        st.warning("⚠️ Brak ceny nabycia towaru lub usługi może skutkować zastosowaniem SKD.")

st.divider()

# --- Podsumowanie naruszeń ---
st.subheader("Podsumowanie naruszeń")
if naruszenia:
    st.error("W Twojej umowie stwierdzono następujące nieprawidłowości:")
    for naruszenie in naruszenia:
        st.write(f"- {naruszenie}")
    st.warning("""
    **Konsekwencje prawne:**  
    Powyższe naruszenia mogą stanowić podstawę do zastosowania sankcji kredytu darmowego (SKD) 
    zgodnie z art. 45 ustawy o kredycie konsumenckim.
    """)
else:
    st.success("""
    ✅ Umowa spełnia wszystkie podstawowe wymogi formalne.  
    Brak stwierdzonych naruszeń przepisów o kredycie konsumenckim.
    """)
st.divider()

# --- Kalkulator MPKK ---
st.header("Kalkulator MPKK", divider="gray")
licz_mpk = st.radio(
    "Czy chcesz policzyć maksymalne pozaodsetkowe koszty kredytu?",
    ["Tak", "Nie"],
    key="licz_mpk"
)

if 'MPKK' not in st.session_state:
    st.session_state.MPKK = None

if licz_mpk == "Tak":
    st.header("Podaj kwotę kredytu", divider="gray")
    st.markdown(
        """
        Kwota kredytu musi mieścić się w przedziale **od 0 do 255&nbsp;550 złotych**,
        chyba że wybrałeś kredyt na remont nieruchomości **(wtedy limit nie obowiązuje)**.
        <br>Możesz wpisać w formacie: <code>100000</code>, <code>100.000</code>, <code>240000,12</code> itp.
        """, unsafe_allow_html=True
    )
    kwota_str = st.text_input("Kwota kredytu:", value="", key="kwota")

    def parse_amount(amount_str):
        amount_str = amount_str.replace(" ", "")
        if "," in amount_str and "." in amount_str:
            amount_str = amount_str.replace(".", "").replace(",", ".")
        elif "," in amount_str:
            amount_str = amount_str.replace(",", ".")
        else:
            amount_str = amount_str.replace(".", "")
        try:
            value = float(amount_str)
            return value
        except ValueError:
            return None

    def format_pln(amount):
        return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    K = parse_amount(kwota_str) if kwota_str else None

    if kwota_str:
        if K is None or K < 0 or (K > 255550 and kredyt != "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości"):
            st.error("Podaj poprawną kwotę kredytu zgodną z limitem.")
            st.stop()

    st.divider()

    st.header("Podaj okres spłaty", divider="gray")
    st.info(
        "Rekomendacja: dla największej precyzji zalecamy wpisywanie okresu spłaty w dniach. "
        "Liczba dni w poszczególnych miesiącach różni się, dlatego podanie okresu w miesiącach może powodować niewielkie rozbieżności w wyniku."
    )

    input_type = st.radio("Wybierz sposób podania okresu spłaty:", ("W miesiącach", "W dniach"), key="okres")

    with st.expander("⚙️ Opcjonalnie: Ustawienia liczby dni w roku i miesiącu"):
        st.markdown(
            """
            Domyślnie rok przyjmowany jest jako **365 dni**, a miesiąc jako **30,42 dnia**.  
            Jeśli Twoja umowa wskazuje inne wartości (np. rok = 360 dni, miesiąc = 30 dni), możesz je zmienić tutaj.
            """
        )
        col1, col2 = st.columns(2)
        with col1:
            days_in_year = st.number_input("Liczba dni w roku:", min_value=1, max_value=400, value=365, step=1, key="dni_rok")
        with col2:
            days_in_month = st.number_input("Liczba dni w miesiącu:", min_value=1.0, max_value=31.0, value=30.42, step=0.01, key="dni_miesiac")

    if days_in_year < 300 or days_in_year > 400:
        st.warning(f"⚠️ Wybrałeś nietypową liczbę dni w roku: {days_in_year} dni. Standardowo przyjmuje się 365.")

    if days_in_month < 25 or days_in_month > 31:
        st.warning(f"⚠️ Wybrałeś nietypową liczbę dni w miesiącu: {days_in_month:.2f} dni. Standardowo przyjmuje się 30,42.")

    if input_type == "W miesiącach":
        months = st.number_input("Okres spłaty (w miesiącach):", min_value=1, step=1, key="miesiace")
        n = months * days_in_month
    else:
        n = st.number_input("Okres spłaty (w dniach):", min_value=1, step=1, key="dni")

    R = days_in_year

    st.divider()

    st.header("Wzór MPKK", divider="gray")
    if choice == "1":
        st.info("**Wybrano wzór:**\nMPKK = (K × 25%) + (K × n/R × 30%)\nMaksymalna wysokość MPKK = całkowita kwota kredytu")
        limit_info = "maksymalna wysokość MPKK = całkowita kwota kredytu"
    elif choice == "2":
        st.info("""**Wybrano wzór:**  
- Dla okresu **krótszego niż 30 dni**: MPKK = K × 5%  
- Dla okresu **równego lub dłuższego niż 30 dni**: MPKK = (K × 15%) + (K × n/R × 6%)  
Maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu""")
        limit_info = "maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu"
    elif choice == "3":
        st.info("**Wybrano wzór:**\nMPKK = (K × 25%) + (K × n/R × 30%)\nMaksymalna wysokość MPKK = całkowita kwota kredytu")
        limit_info = "maksymalna wysokość MPKK = całkowita kwota kredytu"
    elif choice == "4":
        st.info("""**Wybrano wzór:**  
- Dla okresu **krótszego niż 30 dni**: MPKK = K × 5%  
- Dla okresu **równego lub dłuższego niż 30 dni**: MPKK = (K × 10%) + (K × n/R × 10%)  
Maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu""")
        limit_info = "maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu"

    if st.button("Oblicz MPKK"):
        is_short_term = n < 30

        if choice in ["1", "3"]:
            mpkk_wzor = (K * 0.25) + (K * n / R * 0.30)
            formula = "MPKK = (K × 25%) + (K × n/R × 30%)"
            limit = K
        elif choice == "2":
            if is_short_term:
                mpkk_wzor = K * 0.05
                formula = "MPKK = K × 5% (dla okresu krótszego niż 30 dni)"
            else:
                mpkk_wzor = (K * 0.15) + (K * n / R * 0.06)
                formula = "MPKK = (K × 15%) + (K × n/R × 6%) (dla okresu równego lub dłuższego niż 30 dni)"
            limit = K * 0.45
        elif choice == "4":
            if is_short_term:
                mpkk_wzor = K * 0.05
                formula = "MPKK = K × 5% (dla okresu krótszego niż 30 dni)"
            else:
                mpkk_wzor = (K * 0.10) + (K * n / R * 0.10)
                formula = "MPKK = (K × 10%) + (K × n/R × 10%) (dla okresu równego lub dłuższego niż 30 dni)"
            limit = K * 0.45

        MPKK = min(mpkk_wzor, limit)
        st.session_state.MPKK = MPKK

        st.success(f"**Obliczona maksymalna wysokość pozaodsetkowych kosztów kredytu:** {format_pln(MPKK)} zł")
        st.write(f"**Użyty wzór:** {formula}")
        st.write(f"**Wynik MPKK według wzoru:** {format_pln(mpkk_wzor)} zł")

        if mpkk_wzor > limit:
            st.warning(
                f"MPKK według wzoru przekracza limit, {limit_info}. Limit wynosi: {format_pln(limit)} zł"
            )
        else:
            st.info("MPKK według wzoru mieści się w ustawowym limicie.")

    # Pytanie o przekroczenie kosztów PO obliczeniach
    if st.session_state.get('MPKK'):
        st.divider()
        przekroczone = st.radio(
            "Czy suma Twoich rzeczywistych pozaodsetkowych kosztów przekracza obliczony limit?",
            ["Nie", "Tak"],
            key="mpkk_przekroczenie"
        )
        if przekroczone == "Tak":
            naruszenia.append("Przekroczenie limitu MPKK (art. 5 ust. 1 ustawy o kredycie konsumenckim)")
            st.error("❗ Przekroczenie limitu MPKK stanowi podstawę do zastosowania sankcji SKD")

# --- Kalkulator RRSO ---
st.header("Kalkulator RRSO", divider="gray")
licz_rrso = st.radio(
    "Czy chcesz sprawdzić RRSO Twojego kredytu?",
    ["Nie", "Tak"],
    key="licz_rrso"
)

if licz_rrso == "Tak":
    def oblicz_rrso(wyplaty, splaty):
        def funkcja(X):
            lewa = sum(ck / (1 + X)**tk for ck, tk in wyplaty)
            prawa = sum(dl / (1 + X)**sl for dl, sl in splaty)
            return lewa - prawa

        try:
            wynik = newton(funkcja, 0.05, maxiter=1000)
            return round(wynik * 100, 1)
        except RuntimeError:
            return None

    # Sekcja wypłat
    with st.expander("🗓️ Harmonogram wypłat kredytu"):
        m = st.number_input("Liczba transz kredytu:", min_value=1, step=1, key="m_rrso")
        wyplaty = []
        for i in range(int(m)):
            col1, col2 = st.columns(2)
            with col1:
                ck = st.number_input(f"Kwota transzy {i+1} [zł]", key=f"ck_{i}", format="%.2f")
            with col2:
                tk = st.number_input(f"Okres od dziś do wypłaty {i+1} [lata]", 
                                   min_value=0.0, step=0.01, key=f"tk_{i}", format="%.4f")
            wyplaty.append((ck, tk))

    # Sekcja kosztów
    with st.expander("💸 Koszty dodatkowe"):
        prowizja = st.number_input("Prowizja [zł]", min_value=0.0, step=0.01, key="prowizja_rrso")
        oplata_przygotowawcza = st.number_input("Opłata przygotowawcza [zł]", min_value=0.0, step=0.01, key="op_przyg")
        koszt_miesieczny = st.number_input("Koszty cykliczne (miesięczne) [zł]", min_value=0.0, step=0.01, key="koszt_cykliczny")

    # Sekcja spłat
    with st.expander("📅 Harmonogram spłat"):
        rata_stala = st.number_input("Wysokość stałej raty [zł]", min_value=0.0, step=0.01, key="rata_stala")
        liczba_rat_stalych = st.number_input("Liczba stałych rat", min_value=0, step=1, key="l_rat")
        rata_ostatnia = st.number_input("Rata wyrównawcza [zł]", min_value=0.0, step=0.01, key="rata_ost")

    if st.button("Oblicz RRSO"):
        splaty = []

        # Dodaj koszty natychmiastowe
        if prowizja > 0:
            splaty.append((prowizja, 0.0))
        if oplata_przygotowawcza > 0:
            splaty.append((oplata_przygotowawcza, 0.0))

        # Generuj harmonogram spłat
        for i in range(int(liczba_rat_stalych)):
            czas = (i + 1)/12  # konwersja miesięcy na lata
            splaty.append((rata_stala + koszt_miesieczny, czas))
        
        if rata_ostatnia > 0:
            czas_ostatniej = (liczba_rat_stalych + 1)/12
            splaty.append((rata_ostatnia + koszt_miesieczny, czas_ostatniej))

        rrso = oblicz_rrso(wyplaty, splaty)
        
        if rrso:
            st.success(f"**Obliczone RRSO:** {rrso}%")
            st.session_state.rrso_obliczone = rrso
        else:
            st.error("Nie udało się obliczyć RRSO. Sprawdź poprawność danych!")

    # Weryfikacja zgodności z umową
    if st.session_state.get('rrso_obliczone'):
        zgodnosc_rrso = st.radio(
            "Czy RRSO podane w Twojej umowie zgadza się z obliczoną wartością?",
            ["Tak", "Nie"],
            key="zgodnosc_rrso"
        )
        if zgodnosc_rrso == "Nie":
            naruszenia.append("Rozbieżność między RRSO w umowie a rzeczywistymi obliczeniami")
            st.error("❗ Niezgodność RRSO stanowi podstawę do zastosowania SKD (art. 4 ust. 5 ustawy o kredycie konsumenckim)")

# --- Stopka ---
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:0.95rem;">
        Kalkulator nie stanowi porady prawnej.<br>
        W razie wątpliwości skonsultuj się z prawnikiem lub doradcą finansowym.<br>
        <br>
        <span style='font-size:0.85rem;'>Designed by Hubert Domański Salutaris Polska ® 2025</span>
    </div>
    """, 
    unsafe_allow_html=True
)
