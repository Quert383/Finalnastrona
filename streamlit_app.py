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
    pass
    # ... (cała sekcja MPKK z Twojego kodu pozostaje bez zmian) ...

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

    # ... (reszta kodu RRSO z Twojego przykładu) ...

# --- Stopka CAŁY CZAS NA DOLE ---
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
