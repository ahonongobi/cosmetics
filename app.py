import requests
import streamlit as st
import pandas as pd
import altair as alt

# --- Configuration ---
st.set_page_config(page_title="Open Cosmetic Dashboard",
                   page_icon="🧴", layout="wide")
st.title("🧴 Open Cosmetic Data – Dashboard Aperçu")
st.caption(
    "⏱ Données collectées en temps réel depuis Open Beauty Facts (API publique).")

# --- Sélection de catégorie ---
st.sidebar.title("⚙️ Paramètres")
categories = ["soap", "cream", "shampoo", "lipstick", "perfume"]
selected = st.sidebar.selectbox(
    "Choisissez une catégorie :", categories, index=0)

# --- Recherche libre ---
search_term = st.sidebar.text_input("🔍 Rechercher un mot-clé :", selected)

# --- Récupération automatique ---
API_URL = "https://world.openbeautyfacts.org/cgi/search.pl"
params = {
    "search_terms": search_term or selected,
    "search_simple": 1,
    "action": "process",
    "json": 1,
    "page_size": 20,
    "lc": "fr"
}

res = requests.get(API_URL, params=params).json()
products = res.get("products", [])

if not products:
    st.warning("Aucun produit trouvé.")
    st.stop()

# --- Nettoyage des données ---
data = []
for p in products:
    data.append({
        "Nom": p.get("product_name", "Nom inconnu"),
        "Marque": p.get("brands", "Non spécifié"),
        "Catégorie": p.get("categories", selected),
        "Allergènes": p.get("allergens", "Non renseigné"),
        "INCI": p.get("ingredients_text", "Non disponible"),
        "Image": p.get("image_front_url", "")
    })

df = pd.DataFrame(data)

# --- Statistiques en haut du tableau de bord ---
complete = df[df["INCI"] != "Non disponible"].shape[0]
percent = round(complete / len(df) * 100, 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produits collectés", len(df))
col2.metric("Catégorie", selected.capitalize())
col3.metric("Champs analysés", "Nom, Marque, INCI, Allergènes")
col4.metric("Produits complets", f"{complete} ({percent}%)")

st.markdown("---")

# --- Graphique par marque ---
if len(df["Marque"].unique()) > 1:
    chart = (
        alt.Chart(df)
        .mark_bar(color="#6C63FF")
        .encode(
            x=alt.X("Marque", sort="-y", title="Marques"),
            y=alt.Y("count()", title="Nombre de produits")
        )
        .properties(width=700, height=350, title="📊 Répartition des produits par marque")
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown("---")

# --- Affichage sous forme de cartes jolies ---
for i, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])
        if row["Image"]:
            cols[0].image(row["Image"], width=130)
        cols[1].markdown(f"### 🧴 {row['Nom']}")
        cols[1].write(f"**Marque :** {row['Marque']}")

        if row["Allergènes"] and row["Allergènes"] != "Non renseigné":
            cols[1].write(f"**Allergènes :** {row['Allergènes']}")
        else:
            cols[1].write("**Allergènes :** Aucune information disponible")

        if row["INCI"] and row["INCI"] != "Non disponible":
            cols[1].markdown(
                f"**Ingrédients (INCI)** : {row['INCI'][:300]}{'...' if len(row['INCI'])>300 else ''}"
            )
        else:
            cols[1].markdown("**Ingrédients (INCI)** : Non renseignés")
    st.markdown("---")

# --- Export CSV ---
st.download_button(
    label="📥 Télécharger les données (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"open_cosmetic_{selected}.csv",
    mime="text/csv"
)

st.success("✅ Données affichées automatiquement depuis l'API Open Beauty Facts")
