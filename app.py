import streamlit as st
import matplotlib.pyplot as plt

from modules.query_engine import search_data
from modules.translator import normalize_query
from modules.voice_input import get_voice_query

# ------------------- Page Config -------------------
st.set_page_config(page_title="AquaSarthi Prototype", layout="wide")
st.markdown(
    """
    <style>
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .ai-box {
        background: #f1f8e9;
        border-left: 6px solid #2e7d32;
        padding: 10px;
        margin-top: 10px;
        border-radius: 6px;
    }
    .explanation {
        font-style: italic;
        color: #1b5e20;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------- Header -------------------
st.markdown(
    """
    <div style="background:#004d40; padding:15px; border-radius:10px; text-align:center; color:white;">
        <h1>💧 AquaSarthi – AI Chatbot for Groundwater Insights</h1>
        <p>Your smart assistant to query groundwater data in natural language.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------- Session State -------------------
if "query" not in st.session_state:
    st.session_state["query"] = ""
if "last_query_run" not in st.session_state:
    st.session_state["last_query_run"] = None
if "voice_error" not in st.session_state:
    st.session_state["voice_error"] = ""

# ------------------- Voice Callback -------------------
def voice_callback():
    voice_text = get_voice_query()
    st.session_state["query"] = voice_text
    if voice_text.startswith("[voice error]"):
        st.session_state["voice_error"] = voice_text
    else:
        st.session_state["voice_error"] = ""

# ------------------- Input Section -------------------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔎 Ask AquaSarthi")
    query_input = st.text_input("Enter your query:", key="query")
    st.button("🎤 Use Voice Input", on_click=voice_callback)

    if st.session_state.get("voice_error"):
        st.warning(st.session_state["voice_error"])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- Search & Display -------------------
def run_search_and_display(qtext):
    normalized = normalize_query(qtext)
    st.info(f"🔎 Interpreted Query: {normalized}")

    results, filters = search_data(normalized)
    if results is None:
        st.warning(f"No data found for {filters}")
        return

    st.success(f"Showing results for: {filters}")
    st.dataframe(results)

    # --- All Charts in One Row ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Groundwater Insights")

    col1, col2, col3 = st.columns(3)

    # --- Chart 1: Yearly Trend ---
    with col1:
        st.caption("📈 Recharge vs Extraction (Trend)")
        fig1, ax1 = plt.subplots(figsize=(3.5,2.5))
        yearly = results.groupby("year")[["recharge_mm", "extraction_mcm"]].mean()
        if not yearly.empty:
            yearly.plot(ax=ax1, marker="o", linewidth=1.5, color=["#0077b6","#ef476f"])
            ax1.set_title("Trend", fontsize=9)
            ax1.set_xlabel("Year", fontsize=7)
            ax1.set_ylabel("Value", fontsize=7)
            ax1.grid(alpha=0.3)
        st.pyplot(fig1)

    # --- Chart 2: Category Pie ---
    with col2:
        st.caption("🟢 Category Distribution")
        fig2, ax2 = plt.subplots(figsize=(3,2.5))
        cat_counts = results["category"].value_counts()
        if not cat_counts.empty:
            colors = ["#90be6d","#ffd166","#f8961e","#f94144"]
            ax2.pie(cat_counts, labels=cat_counts.index, autopct="%1.0f%%", startangle=90,
                    colors=colors, textprops={'fontsize':7})
            ax2.set_title("Category Split", fontsize=9)
        st.pyplot(fig2)

    # --- Chart 3: Scatter Plot ---
    with col3:
        st.caption("🔵 Recharge vs Extraction (Scatter)")
        fig3, ax3 = plt.subplots(figsize=(3.5,2.5))
        if not results.empty:
            ax3.scatter(results["recharge_mm"], results["extraction_mcm"],
                        c="#118ab2", alpha=0.6, s=20, edgecolors="white", linewidths=0.5)
            ax3.set_xlabel("Recharge (mm)", fontsize=7)
            ax3.set_ylabel("Extraction (mcm)", fontsize=7)
            ax3.set_title("Scatter", fontsize=9)
            ax3.grid(alpha=0.3)
        st.pyplot(fig3)

    # --- Combined AI Explanation ---
    if not results.empty:
        exp_text = []

        # Trend
        yearly = results.groupby("year")[["recharge_mm", "extraction_mcm"]].mean()
        if not yearly.empty:
            diff = yearly["extraction_mcm"].mean() - yearly["recharge_mm"].mean()
            if diff > 0:
                exp_text.append("⚠️ Extraction is generally higher than recharge → groundwater stress.")
            else:
                exp_text.append("✅ Recharge is generally higher than extraction → sustainable usage.")

        # Categories
        if not cat_counts.empty:
            dom_cat = cat_counts.idxmax()
            exp_text.append(f"Most areas fall under **{dom_cat}** category → reflects groundwater condition.")

        # Correlation
        if "recharge_mm" in results.columns and "extraction_mcm" in results.columns:
            corr = results["recharge_mm"].corr(results["extraction_mcm"])
            if corr > 0.7:
                exp_text.append("📊 Higher recharge strongly correlates with higher extraction → heavy exploitation.")
            else:
                exp_text.append("📊 Recharge and extraction are weakly correlated → usage not always linked with recharge.")

        if exp_text:
            st.markdown(f"<div class='ai-box'><p class='explanation'>{'<br>'.join(exp_text)}</p></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Compare Water Level Section ---
    if "show_compare" not in st.session_state:
        st.session_state.show_compare = False

    if st.button("Compare Water Level"):
        st.session_state.show_compare = True

    if st.session_state.show_compare:
        st.subheader("🔄 Compare Groundwater Levels")

        # Dropdown options from data
        states = results["state"].unique().tolist()
        years = sorted(results["year"].unique().tolist())

        # State selection
        state_sel = st.selectbox("Select State", states, key="cmp_state")

        # Districts filtered by state
        filtered_districts = results[results["state"] == state_sel]["district"].unique().tolist()

        col1, col2 = st.columns(2)
        with col1:
            district_sel = st.selectbox("Select District", filtered_districts, key="cmp_district")
            year1 = st.selectbox("Select Year 1", years, key="cmp_year1")
        with col2:
            year2 = st.selectbox("Select Year 2", years, key="cmp_year2")

        if st.button("📊 Compare"):
            comp_data = results[
                (results["state"] == state_sel) &
                (results["district"] == district_sel) &
                (results["year"].isin([year1, year2]))
            ]

            if comp_data.empty:
                st.warning("⚠️ No data found for this selection.")
            else:
                st.subheader(f"Comparison for {district_sel}, {state_sel}")
                fig, ax = plt.subplots(figsize=(5,3))

                recharge_vals = [
                    comp_data[comp_data["year"]==year1]["recharge_mm"].mean(),
                    comp_data[comp_data["year"]==year2]["recharge_mm"].mean()
                ]
                extraction_vals = [
                    comp_data[comp_data["year"]==year1]["extraction_mcm"].mean(),
                    comp_data[comp_data["year"]==year2]["extraction_mcm"].mean()
                ]

                ax.bar([str(year1), str(year2)], recharge_vals, color="blue", alpha=0.6, label="Recharge")
                ax.bar([str(year1), str(year2)], extraction_vals, color="red", alpha=0.6, label="Extraction")
                ax.legend()
                ax.set_ylabel("Values")
                st.pyplot(fig)

                # AI-style explanation
                exp_text = []
                if recharge_vals[0] > recharge_vals[1]:
                    exp_text.append(f"💧 Recharge decreased from {year1} ({recharge_vals[0]:.1f}) to {year2} ({recharge_vals[1]:.1f}).")
                else:
                    exp_text.append(f"💧 Recharge increased from {year1} ({recharge_vals[0]:.1f}) to {year2} ({recharge_vals[1]:.1f}).")

                if extraction_vals[0] > extraction_vals[1]:
                    exp_text.append(f"⚠️ Extraction decreased from {year1} ({extraction_vals[0]:.1f}) to {year2} ({extraction_vals[1]:.1f}).")
                else:
                    exp_text.append(f"⚠️ Extraction increased from {year1} ({extraction_vals[0]:.1f}) to {year2} ({extraction_vals[1]:.1f}).")

                st.markdown(f"<div class='ai-box'><p class='explanation'>{'<br>'.join(exp_text)}</p></div>", unsafe_allow_html=True)

    # --- Compare Water Level Section ---
    if "show_compare" not in st.session_state:
        st.session_state.show_compare = False

    if st.button("Compare Water Level"):
        st.session_state.show_compare = True

    if st.session_state.show_compare:
        st.subheader("🔄 Compare Groundwater Levels")

        # Dropdown options from data
        states = results["state"].unique().tolist()
        years = sorted(results["year"].unique().tolist())

        # State selection
        state_sel = st.selectbox("Select State", states, key="cmp_state")

        # Districts filtered by state
        filtered_districts = results[results["state"] == state_sel]["district"].unique().tolist()

        col1, col2 = st.columns(2)
        with col1:
            district_sel = st.selectbox("Select District", filtered_districts, key="cmp_district")
            year1 = st.selectbox("Select Year 1", years, key="cmp_year1")
        with col2:
            year2 = st.selectbox("Select Year 2", years, key="cmp_year2")

        if st.button("📊 Compare"):
            comp_data = results[
                (results["state"] == state_sel) &
                (results["district"] == district_sel) &
                (results["year"].isin([year1, year2]))
            ]

            if comp_data.empty:
                st.warning("⚠️ No data found for this selection.")
            else:
                st.subheader(f"Comparison for {district_sel}, {state_sel}")
                fig, ax = plt.subplots(figsize=(5,3))

                recharge_vals = [
                    comp_data[comp_data["year"]==year1]["recharge_mm"].mean(),
                    comp_data[comp_data["year"]==year2]["recharge_mm"].mean()
                ]
                extraction_vals = [
                    comp_data[comp_data["year"]==year1]["extraction_mcm"].mean(),
                    comp_data[comp_data["year"]==year2]["extraction_mcm"].mean()
                ]

                ax.bar([str(year1), str(year2)], recharge_vals, color="blue", alpha=0.6, label="Recharge")
                ax.bar([str(year1), str(year2)], extraction_vals, color="red", alpha=0.6, label="Extraction")
                ax.legend()
                ax.set_ylabel("Values")
                st.pyplot(fig)

                # AI-style explanation
                exp_text = []
                if recharge_vals[0] > recharge_vals[1]:
                    exp_text.append(f"💧 Recharge decreased from {year1} ({recharge_vals[0]:.1f}) to {year2} ({recharge_vals[1]:.1f}).")
                else:
                    exp_text.append(f"💧 Recharge increased from {year1} ({recharge_vals[0]:.1f}) to {year2} ({recharge_vals[1]:.1f}).")

                if extraction_vals[0] > extraction_vals[1]:
                    exp_text.append(f"⚠️ Extraction decreased from {year1} ({extraction_vals[0]:.1f}) to {year2} ({extraction_vals[1]:.1f}).")
                else:
                    exp_text.append(f"⚠️ Extraction increased from {year1} ({extraction_vals[0]:.1f}) to {year2} ({extraction_vals[1]:.1f}).")

                st.markdown(f"<div class='ai-box'><p class='explanation'>{'<br>'.join(exp_text)}</p></div>", unsafe_allow_html=True)

# ------------------- Auto-run Query -------------------
current_query = st.session_state.get("query", "").strip()
if current_query and st.session_state.get("last_query_run") != current_query:
    if not current_query.startswith("[voice error]"):
        run_search_and_display(current_query)
        st.session_state["last_query_run"] = current_query

