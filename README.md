# A pénz időértéke – Streamlit gyakorlófelület

Ez az app a „Pénzügyi Menedzsment – A pénz időértéke, speciális pénzáramlások” típusú számítási feladatok gyakorlására készült.

## Tartalom

NPV nélkül tartalmazza az alábbi feladattípusokat:

- egyszerű kamatszámítás,
- törtéves kamatszámítás 365 napos évvel,
- egyszerű és kamatos kamat összehasonlítása,
- jelenérték és diszkontfaktor,
- célösszeghez szükséges időtáv,
- effektív éves hozam,
- örökjáradék, előleges és halasztott örökjáradék,
- annuitás jelenértéke,
- kamatmentes részletfizetés jelenértéke,
- halasztott annuitás,
- növekvő örökjáradék,
- tőkésítési gyakoriság hatása.

## Helyi futtatás

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Hozzon létre GitHubon egy új repót.
2. Töltse fel az `app.py`, `requirements.txt` és `README.md` fájlokat.
3. Streamlit Community Cloudban válassza ki a repót.
4. Main file path: `app.py`
5. Deploy.
