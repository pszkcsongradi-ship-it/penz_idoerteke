import math
import random
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="A pénz időértéke – gyakorlófelület",
    page_icon="⏳",
    layout="wide"
)

# -----------------------------
# Alapfüggvények
# -----------------------------

def fv_simple(pv, r, n):
    return pv * (1 + r * n)

def fv_compound(pv, r, n):
    return pv * (1 + r) ** n

def pv_single(fv, r, n):
    return fv / (1 + r) ** n

def discount_factor(r, n):
    return 1 / (1 + r) ** n

def years_to_target(pv, fv, r):
    return math.log(fv / pv) / math.log(1 + r)

def effective_rate(pv, fv, n):
    return (fv / pv) ** (1 / n) - 1

def fv_nominal_compounding(pv, nominal_r, years, m):
    return pv * (1 + nominal_r / m) ** (m * years)

def pv_annuity(c, r, n):
    if r == 0:
        return c * n
    return c * (1 - (1 + r) ** (-n)) / r

def pv_annuity_due(c, r, n):
    return pv_annuity(c, r, n) * (1 + r)

def pv_perpetuity(c, r):
    if r <= 0:
        return float("nan")
    return c / r

def pv_perpetuity_due(c, r):
    return pv_perpetuity(c, r) * (1 + r)

def pv_deferred_perpetuity(c, r, first_payment_period):
    # first payment at t = k. Ordinary perpetuity value one period before first payment: C/r at t=k-1.
    return (c / r) / ((1 + r) ** (first_payment_period - 1))

def pv_growing_perpetuity_first_payment(c1, r, g, first_payment_period=1):
    # value one period before first payment: C1/(r-g)
    if r <= g:
        return float("nan")
    return (c1 / (r - g)) / ((1 + r) ** (first_payment_period - 1))

def money(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "nem értelmezhető"
    return f"{x:,.0f} Ft".replace(",", " ")

def money_currency(x, currency="Ft"):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "nem értelmezhető"
    return f"{x:,.0f} {currency}".replace(",", " ")

def pct(x):
    return f"{x*100:.2f}%"

def close_enough(user_value, correct_value, tolerance_pct=0.01, min_tol=10):
    tolerance = max(abs(correct_value) * tolerance_pct, min_tol)
    return abs(user_value - correct_value) <= tolerance

def init_state():
    defaults = {
        "score_ok": 0,
        "score_total": 0,
        "task": None,
        "checked": False,
        "selected_categories": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -----------------------------
# Feladatgenerátorok
# -----------------------------

TASK_CATEGORIES = [
    "Egyszerű kamatozás – éves kamat nem tőkésül",
    "Törtéves egyszerű kamatozás – napszámítással",
    "Egyszerű és kamatos kamat összehasonlítása",
    "Jelenérték és diszkontfaktor",
    "Időtáv meghatározása célösszeghez",
    "Effektív éves hozam meghatározása",
    "Örökjáradék, előleges és halasztott örökjáradék",
    "Annuitás jelenértéke",
    "Kamatmentes részlet vs. árengedmény",
    "Halasztott annuitás jelenértéke",
    "Növekvő örökjáradék jelenértéke",
    "Tőkésítési gyakoriság hatása"
]

def generate_task(categories=None):
    if not categories:
        categories = TASK_CATEGORIES
    task_type = random.choice(categories)

    if task_type == "Egyszerű kamatozás – éves kamat nem tőkésül":
        pv = random.choice([500000, 1000000, 1500000, 2000000, 5000000])
        r = random.choice([0.04, 0.05, 0.06, 0.07, 0.08, 0.10])
        n = random.choice([1, 2, 3, 4, 5])
        ans = fv_simple(pv, r, n)
        return {
            "type": task_type,
            "question": f"Mekkora összeg lesz a számlán {n} év múlva, ha {money(pv)} összeget {pct(r)} éves kamatláb mellett helyezünk el, és az éves kamatokat nem tőkésítik?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"Egyszerű kamatozásnál FV = PV × (1 + r × n). Ezért FV = {money(pv)} × (1 + {r:.2f} × {n}) = {money(ans)}."
        }

    if task_type == "Törtéves egyszerű kamatozás – napszámítással":
        pv = random.choice([500000, 1000000, 2500000, 5000000, 8000000])
        r = random.choice([0.06, 0.08, 0.10, 0.12, 0.15])
        days = random.choice([30, 60, 90, 120, 122, 180, 270])
        ans = fv_simple(pv, r, days / 365)
        return {
            "type": task_type,
            "question": f"Mekkora lesz {money(pv)} értéke {days} nap múlva, ha az éves betéti kamatláb {pct(r)}, és a bank 365 napos évvel számol?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"A törtéves időtáv n = {days}/365. FV = PV × (1 + r × n) = {money(pv)} × (1 + {r:.2f} × {days}/365) = {money(ans)}."
        }

    if task_type == "Egyszerű és kamatos kamat összehasonlítása":
        pv = random.choice([500000, 1000000, 2000000])
        annual_r = random.choice([0.06, 0.08, 0.10, 0.12, 0.15])
        months = random.choice([3, 4, 6, 9, 12, 24, 36])
        n = months / 12
        simple = fv_simple(pv, annual_r, n)
        compound = fv_compound(pv, annual_r, n)
        diff = compound - simple
        return {
            "type": task_type,
            "question": f"Számítsa ki {money(pv)} tőkeértékét egyszerű és kamatos kamatozással {months} hónapra, ha az éves kamatláb {pct(annual_r)}! A válaszmezőbe a kamatos kamatozás szerinti értéket írja.",
            "answer": compound,
            "unit": "Ft",
            "explanation": f"Egyszerű: {money(simple)}. Kamatos: FV = {money(pv)} × (1+{annual_r:.2f})^({months}/12) = {money(compound)}. A különbség: {money(diff)}."
        }

    if task_type == "Jelenérték és diszkontfaktor":
        fv = random.choice([800000, 1000000, 1300000, 1500000, 2000000, 5000000])
        r = random.choice([0.06, 0.08, 0.10, 0.12, 0.15])
        n = random.choice([1, 2, 3, 4, 5])
        pv = pv_single(fv, r, n)
        df = discount_factor(r, n)
        return {
            "type": task_type,
            "question": f"Mennyi a jelenértéke {money(fv)} összegnek, ha {n} év múlva esedékes, és az elvárt hozam {pct(r)}? A válaszmezőbe a jelenértéket írja.",
            "answer": pv,
            "unit": "Ft",
            "explanation": f"Diszkontfaktor = 1/(1+r)^n = 1/(1+{r:.2f})^{n} = {df:.4f}. PV = FV × diszkontfaktor = {money(fv)} × {df:.4f} = {money(pv)}."
        }

    if task_type == "Időtáv meghatározása célösszeghez":
        pv = random.choice([5000000, 7000000, 10000000])
        fv = random.choice([20000000, 30000000, 40000000, 50000000])
        r = random.choice([0.06, 0.08, 0.10, 0.12])
        ans = years_to_target(pv, fv, r)
        return {
            "type": task_type,
            "question": f"Hány évig kell befektetni {money(pv)} összeget, hogy {money(fv)} legyen belőle, ha az éves átlaghozam {pct(r)}? A választ évben adja meg.",
            "answer": ans,
            "unit": "év",
            "explanation": f"FV = PV × (1+r)^n, ebből n = ln(FV/PV) / ln(1+r). n = ln({fv}/{pv}) / ln(1+{r:.2f}) = {ans:.2f} év."
        }

    if task_type == "Effektív éves hozam meghatározása":
        pv = random.choice([500000, 1000000, 2000000])
        n = random.choice([2, 3, 4, 5])
        r_real = random.choice([0.05, 0.06, 0.07, 0.08, 0.10])
        fv = fv_compound(pv, r_real, n)
        ans = effective_rate(pv, fv, n)
        return {
            "type": task_type,
            "question": f"Mekkora az éves effektív hozam, ha most {money(pv)} összeget helyezünk el, és {n} év múlva {money(fv)} összeget kapunk vissza? A választ százalékban adja meg.",
            "answer": ans * 100,
            "unit": "%",
            "explanation": f"FV = PV × (1+r)^n, ebből r = (FV/PV)^(1/n) - 1. r = ({fv:.0f}/{pv})^(1/{n}) - 1 = {pct(ans)}."
        }

    if task_type == "Örökjáradék, előleges és halasztott örökjáradék":
        c = random.choice([1000000, 2000000, 5000000, 7500000])
        r = random.choice([0.06, 0.08, 0.10, 0.12])
        variant = random.choice(["első kifizetés 1 év múlva", "első kifizetés most", "első kifizetés 4 év múlva"])
        if variant == "első kifizetés 1 év múlva":
            ans = pv_perpetuity(c, r)
            expl = f"Normál örökjáradék: PV = C/r = {money(c)}/{r:.2f} = {money(ans)}."
        elif variant == "első kifizetés most":
            ans = pv_perpetuity_due(c, r)
            expl = f"Előleges örökjáradék: PV = C + C/r = C/r × (1+r) = {money(ans)}."
        else:
            ans = pv_deferred_perpetuity(c, r, 4)
            expl = f"Halasztott örökjáradék: az első kifizetés t=4, ezért az érték t=3-ban C/r, majd ezt 3 évvel diszkontáljuk: PV = (C/r)/(1+r)^3 = {money(ans)}."
        return {
            "type": task_type,
            "question": f"Egy örökjáradék évente {money(c)} összeget fizet. Az elvárt hozam {pct(r)}, az {variant}. Mennyit ér ma?",
            "answer": ans,
            "unit": "Ft",
            "explanation": expl
        }

    if task_type == "Annuitás jelenértéke":
        c = random.choice([50000, 100000, 200000, 500000, 1000000, 5000000])
        r = random.choice([0.01, 0.05, 0.08, 0.10, 0.12])
        n = random.choice([3, 5, 10, 12, 24, 36])
        ans = pv_annuity(c, r, n)
        period = "havi" if r <= 0.02 else "éves"
        return {
            "type": task_type,
            "question": f"Mennyi a jelenértéke egy {n} időszakon keresztül fizetett, időszakonként {money(c)} összegű annuitásnak, ha az elvárt {period} hozam {pct(r)}?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"PV = C × [1 - (1+r)^(-n)] / r = {money(c)} × [1 - (1+{r:.2f})^(-{n})] / {r:.2f} = {money(ans)}."
        }

    if task_type == "Kamatmentes részlet vs. árengedmény":
        price = random.choice([120000, 180000, 240000, 300000, 360000])
        months = random.choice([12, 18, 24, 36])
        payment = price / months
        r = random.choice([0.008, 0.01, 0.012, 0.015])
        discount_pct = random.choice([0.08, 0.10, 0.12, 0.15])
        pv_installments = pv_annuity(payment, r, months)
        cash_discount_price = price * (1 - discount_pct)
        equivalent_discount = 1 - pv_installments / price
        # User answers equivalent discount in percent
        return {
            "type": task_type,
            "question": f"Egy termék ára {money(price)}. Választható {months} havi kamatmentes részlet, havi {money(payment)} fizetéssel, vagy {discount_pct*100:.0f}% azonnali árengedmény. A havi elvárt hozam {pct(r)}. A részletfizetés mekkora árengedménynek felel meg? A választ százalékban adja meg.",
            "answer": equivalent_discount * 100,
            "unit": "%",
            "explanation": f"A részletek jelenértéke: {money(pv_installments)}. Ez az eredeti árhoz képest {(equivalent_discount*100):.2f}% árengedménynek felel meg. Az azonnali kuponos ár: {money(cash_discount_price)}."
        }

    if task_type == "Halasztott annuitás jelenértéke":
        c = random.choice([30000, 50000, 100000, 150000, 200000])
        r = random.choice([0.008, 0.01, 0.012, 0.015])
        n = random.choice([24, 60, 120])
        first_payment = random.choice([2, 3, 4, 5, 6])
        # ordinary annuity value one period before first payment
        value_at_before_first = pv_annuity(c, r, n)
        ans = value_at_before_first / ((1 + r) ** (first_payment - 1))
        return {
            "type": task_type,
            "question": f"Egy beruházás {n} hónapon keresztül havi {money(c)} megtakarítást eredményez. Az első megtakarítás {first_payment}. hónap múlva jelentkezik. A havi elvárt hozam {pct(r)}. Legfeljebb mennyit érdemes most fizetni érte?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"Először kiszámítjuk a {n} havi annuitás értékét az első kifizetés előtti időpontra: {money(value_at_before_first)}. Mivel az első kifizetés t={first_payment}, ezt {first_payment-1} hónappal diszkontáljuk: PV = {money(ans)}."
        }

    if task_type == "Növekvő örökjáradék jelenértéke":
        c1 = random.choice([500000, 750000, 1000000, 2000000])
        r = random.choice([0.055, 0.058, 0.06, 0.07, 0.08])
        g = random.choice([0.02, 0.03, 0.04])
        first_payment = random.choice([1, 3, 5])
        if g >= r:
            g = r - 0.01
        ans = pv_growing_perpetuity_first_payment(c1, r, g, first_payment)
        return {
            "type": task_type,
            "question": f"Egy növekvő örökjáradék első kifizetése {money(c1)}, amely évente {g*100:.1f}%-kal nő. Az elvárt hozam {pct(r)}, az első kifizetés {first_payment} év múlva esedékes. Mennyit ér ma?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"Növekvő örökjáradék értéke egy periódussal az első kifizetés előtt: C1/(r-g). Ezt {first_payment-1} évvel kell jelenértékre hozni. PV = {money(ans)}."
        }

    if task_type == "Tőkésítési gyakoriság hatása":
        pv = random.choice([500000, 1000000, 2000000])
        nominal_r = random.choice([0.04, 0.06, 0.08, 0.10])
        years = random.choice([1, 2, 3, 5])
        m = random.choice([1, 2, 4, 12])
        ans = fv_nominal_compounding(pv, nominal_r, years, m)
        freq_text = {1: "évente", 2: "félévente", 4: "negyedévente", 12: "havonta"}[m]
        return {
            "type": task_type,
            "question": f"Mekkora összeggel rendelkezünk {years} év múlva, ha {money(pv)} összeget helyezünk el {nominal_r*100:.1f}% éves névleges kamatláb mellett, és a bank a kamatokat {freq_text} tőkésíti?",
            "answer": ans,
            "unit": "Ft",
            "explanation": f"FV = PV × (1 + r/m)^(m×n), ahol m={m}. FV = {money(pv)} × (1+{nominal_r:.2f}/{m})^({m}×{years}) = {money(ans)}."
        }

# -----------------------------
# App
# -----------------------------

init_state()

st.title("⏳ A pénz időértéke – gyakorlófelület")
st.caption("© Csongrádi")

tab1, tab2, tab3, tab4 = st.tabs([
    "Gyakorló feladatok",
    "Interaktív kalkulátor",
    "Képlettár",
    "Oktatói beállítások"
])

with tab1:
    st.header("Véletlen gyakorlófeladatok")

    with st.expander("Feladattípusok kiválasztása", expanded=False):
        selected = st.multiselect(
            "Mely feladattípusokból generáljon példát az app?",
            TASK_CATEGORIES,
            default=TASK_CATEGORIES[:]
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Helyes válasz", st.session_state.score_ok)
    c2.metric("Összes próbálkozás", st.session_state.score_total)
    acc = (st.session_state.score_ok / st.session_state.score_total * 100) if st.session_state.score_total else 0
    c3.metric("Pontosság", f"{acc:.1f}%")

    if st.button("Új feladat generálása") or st.session_state.task is None:
        st.session_state.task = generate_task(selected)
        st.session_state.checked = False

    task = st.session_state.task
    st.info(task["type"])
    st.write(task["question"])

    step = 0.01 if task["unit"] in ["%", "év"] else 1000.0
    user_answer = st.number_input(f"Saját válasz ({task['unit']})", value=0.0, step=step, format="%.4f")

    if st.button("Ellenőrzés"):
        st.session_state.score_total += 1
        st.session_state.checked = True

        correct = task["answer"]
        if close_enough(user_answer, correct, tolerance_pct=0.01, min_tol=0.05 if task["unit"] in ["%", "év"] else 10):
            st.session_state.score_ok += 1
            st.success(f"Helyes válasz. A pontos érték: {correct:.4f} {task['unit']}" if task["unit"] in ["%", "év"] else f"Helyes válasz. A pontos érték: {money(correct)}.")
        else:
            st.error(f"Nem pontos. A helyes érték: {correct:.4f} {task['unit']}" if task["unit"] in ["%", "év"] else f"Nem pontos. A helyes érték: {money(correct)}.")
        st.write(task["explanation"])

with tab2:
    st.header("Interaktív kalkulátor és szemléltetés")

    calc_type = st.selectbox(
        "Számítás típusa",
        [
            "Egyszerű kamatozás",
            "Kamatos kamatozás",
            "Jelenérték és diszkontfaktor",
            "Annuitás jelenértéke",
            "Örökjáradék",
            "Tőkésítési gyakoriság összehasonlítása"
        ]
    )

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        if calc_type in ["Egyszerű kamatozás", "Kamatos kamatozás"]:
            pv = st.number_input("Kezdő összeg", min_value=0.0, value=1000000.0, step=50000.0)
            r = st.slider("Éves kamatláb (%)", 0.0, 30.0, 7.0, 0.5) / 100
            n = st.slider("Évek száma", 0.0, 40.0, 3.0, 0.5)
            result = fv_simple(pv, r, n) if calc_type == "Egyszerű kamatozás" else fv_compound(pv, r, n)
            st.metric("Jövőérték", money(result))
            years = [x for x in range(0, int(max(n, 1)) + 1)]
            simple_vals = [fv_simple(pv, r, y) for y in years]
            compound_vals = [fv_compound(pv, r, y) for y in years]

        elif calc_type == "Jelenérték és diszkontfaktor":
            fv = st.number_input("Jövőbeli összeg", min_value=0.0, value=1300000.0, step=50000.0)
            r = st.slider("Elvárt hozam (%)", 0.0, 30.0, 12.0, 0.5) / 100
            n = st.slider("Évek száma", 0.0, 30.0, 2.0, 0.5)
            result = pv_single(fv, r, n)
            df = discount_factor(r, n)
            st.metric("Jelenérték", money(result))
            st.metric("Diszkontfaktor", f"{df:.4f}")

        elif calc_type == "Annuitás jelenértéke":
            c = st.number_input("Időszaki pénzáram", min_value=0.0, value=100000.0, step=10000.0)
            r = st.slider("Időszaki elvárt hozam (%)", 0.0, 10.0, 1.0, 0.1) / 100
            n = st.slider("Időszakok száma", 1, 240, 24)
            result = pv_annuity(c, r, n)
            st.metric("Annuitás jelenértéke", money(result))

        elif calc_type == "Örökjáradék":
            c = st.number_input("Éves pénzáram", min_value=0.0, value=5000000.0, step=100000.0)
            r = st.slider("Elvárt hozam (%)", 0.1, 30.0, 10.0, 0.5) / 100
            mode = st.radio("Kifizetés időzítése", ["Első kifizetés 1 év múlva", "Első kifizetés most", "Első kifizetés 4 év múlva"])
            if mode == "Első kifizetés 1 év múlva":
                result = pv_perpetuity(c, r)
            elif mode == "Első kifizetés most":
                result = pv_perpetuity_due(c, r)
            else:
                result = pv_deferred_perpetuity(c, r, 4)
            st.metric("Jelenérték", money(result))

        else:
            pv = st.number_input("Kezdő összeg", min_value=0.0, value=500000.0, step=50000.0)
            nominal_r = st.slider("Éves névleges kamatláb (%)", 0.0, 30.0, 6.0, 0.5) / 100
            years = st.slider("Évek száma", 1, 10, 2)
            rows = []
            for m, name in [(1, "éves"), (2, "féléves"), (4, "negyedéves"), (12, "havi")]:
                rows.append({"Tőkésítés": name, "Jövőérték": fv_nominal_compounding(pv, nominal_r, years, m)})
            df_comp = pd.DataFrame(rows)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("Grafikus szemléltetés")
        fig, ax = plt.subplots()

        if calc_type in ["Egyszerű kamatozás", "Kamatos kamatozás"]:
            ax.plot(years, simple_vals, marker="o", label="Egyszerű kamat")
            ax.plot(years, compound_vals, marker="o", label="Kamatos kamat")
            ax.set_xlabel("Év")
            ax.set_ylabel("Érték")
            ax.set_title("Egyszerű és kamatos kamatozás összehasonlítása")
            ax.legend()
        elif calc_type == "Jelenérték és diszkontfaktor":
            xs = list(range(0, int(max(n, 1)) + 1))
            vals = [pv_single(fv, r, x) for x in xs]
            ax.plot(xs, vals, marker="o")
            ax.set_xlabel("Hátralévő évek száma")
            ax.set_ylabel("Jelenérték")
            ax.set_title("A jelenérték csökkenése az időtávval")
        elif calc_type == "Annuitás jelenértéke":
            xs = list(range(1, n + 1))
            vals = [c / (1 + r) ** x for x in xs]
            ax.bar(xs, vals)
            ax.set_xlabel("Időszak")
            ax.set_ylabel("Diszkontált pénzáram")
            ax.set_title("Annuitás pénzáramainak jelenértéke")
        elif calc_type == "Örökjáradék":
            rates = [i / 100 for i in range(1, 31)]
            vals = [pv_perpetuity(c, rr) for rr in rates]
            ax.plot([rr * 100 for rr in rates], vals)
            ax.set_xlabel("Elvárt hozam (%)")
            ax.set_ylabel("Jelenérték")
            ax.set_title("Örökjáradék értéke különböző hozamok mellett")
        else:
            ax.bar(df_comp["Tőkésítés"], df_comp["Jövőérték"])
            ax.set_xlabel("Tőkésítési gyakoriság")
            ax.set_ylabel("Jövőérték")
            ax.set_title("Tőkésítési gyakoriság hatása")

        st.pyplot(fig)

with tab3:
    st.header("Képlettár")

    formulas = pd.DataFrame([
        {"Téma": "Egyszerű kamat", "Képlet": "FV = PV × (1 + r × n)", "Mikor használjuk?": "Ha a kamat nem tőkésül."},
        {"Téma": "Kamatos kamat", "Képlet": "FV = PV × (1+r)^n", "Mikor használjuk?": "Ha a kamat minden időszak végén tőkésül."},
        {"Téma": "Törtéves egyszerű kamat", "Képlet": "FV = PV × (1 + r × napok/365)", "Mikor használjuk?": "Rövid, napon belül megadott betéti időszakoknál."},
        {"Téma": "Jelenérték", "Képlet": "PV = FV / (1+r)^n", "Mikor használjuk?": "Jövőbeli összeg mai értékének meghatározásakor."},
        {"Téma": "Diszkontfaktor", "Képlet": "DF = 1 / (1+r)^n", "Mikor használjuk?": "Megmutatja, mennyit ér ma 1 jövőbeli pénzegység."},
        {"Téma": "Időtáv", "Képlet": "n = ln(FV/PV) / ln(1+r)", "Mikor használjuk?": "Ha a célösszeghez szükséges évek számát keressük."},
        {"Téma": "Effektív éves hozam", "Képlet": "r = (FV/PV)^(1/n) - 1", "Mikor használjuk?": "Ha ismert a kezdő- és végérték."},
        {"Téma": "Annuitás jelenértéke", "Képlet": "PV = C × [1 - (1+r)^(-n)] / r", "Mikor használjuk?": "Azonos időközönként azonos összegű pénzáramoknál."},
        {"Téma": "Örökjáradék", "Képlet": "PV = C / r", "Mikor használjuk?": "Végtelen ideig tartó azonos pénzáramoknál."},
        {"Téma": "Növekvő örökjáradék", "Képlet": "PV = C1 / (r-g)", "Mikor használjuk?": "Végtelen ideig tartó, állandó ütemben növekvő pénzáramnál."},
        {"Téma": "Névleges kamat tőkésítéssel", "Képlet": "FV = PV × (1 + r/m)^(m×n)", "Mikor használjuk?": "Éves névleges kamatláb és éven belüli tőkésítés esetén."}
    ])

    st.dataframe(formulas, use_container_width=True, hide_index=True)

with tab4:
    st.header("Oktatói beállítások és felhasználási javaslat")

    st.markdown("""
    **A felület a következő feladattípusokra épül:**

    - egyszerű kamatszámítás,
    - törtéves kamatszámítás 365 napos évvel,
    - egyszerű és kamatos kamat összehasonlítása,
    - jelenérték és diszkontfaktor,
    - célösszeghez szükséges időtáv,
    - effektív éves hozam,
    - örökjáradék és halasztott örökjáradék,
    - annuitás,
    - kamatmentes részletfizetés jelenértéke,
    - halasztott annuitás,
    - növekvő örökjáradék,
    - tőkésítési gyakoriság.
    """)

    if st.button("Pontszám nullázása"):
        st.session_state.score_ok = 0
        st.session_state.score_total = 0
        st.success("A pontszám nullázva.")
