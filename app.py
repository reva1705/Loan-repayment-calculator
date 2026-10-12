import altair as alt
import pandas as pd
import streamlit as st

from calculator import loan_summary, schedule

# ---------------------------------------------------------------
# Page setup and brand
# ---------------------------------------------------------------
st.set_page_config(page_title="Loan Repayment Calculator", page_icon="🏠", layout="wide")

NAVY = "#0B2545"
INK = "#1B2433"
MUTED = "#5B6577"
AMBER = "#E09F3E"
SKY = "#8DA9C4"
PAPER = "#F4F6FA"
LINE = "#E1E6EE"

st.markdown(f"""
<style>
  .block-container {{ padding-top: 2rem; max-width: 1200px; }}
  h1, h2, h3 {{ color: {NAVY}; letter-spacing: -0.01em; }}

  .hero {{ display: flex; align-items: center; justify-content: space-between; gap: 24px;
          background: linear-gradient(135deg, {NAVY} 0%, #13315C 100%);
          border-radius: 18px; padding: 28px 36px; margin-bottom: 28px; }}
  .hero .eyebrow {{ color: {AMBER}; font-size: .78rem; font-weight: 700;
                   letter-spacing: .14em; text-transform: uppercase; margin: 0 0 6px; }}
  .hero h1 {{ color: #FFFFFF; font-size: 2.1rem; margin: 0 0 8px; padding: 0; }}
  .hero p {{ color: #C9D6E6; margin: 0; max-width: 560px; font-size: 1rem; }}
  .hero svg {{ flex-shrink: 0; }}
  @media (max-width: 760px) {{ .hero svg {{ display: none; }} }}

  .kpi {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 14px;
          padding: 18px 20px; display: flex; gap: 14px; align-items: center; height: 100%; }}
  .kpi .icon {{ width: 46px; height: 46px; border-radius: 12px; background: {PAPER};
               display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .kpi .label {{ color: {MUTED}; font-size: .78rem; font-weight: 600;
                text-transform: uppercase; letter-spacing: .06em; }}
  .kpi .value {{ color: {NAVY}; font-size: 1.55rem; font-weight: 700; line-height: 1.2; }}
  .kpi.primary {{ background: {NAVY}; border-color: {NAVY}; }}
  .kpi.primary .label {{ color: #C9D6E6; }}
  .kpi.primary .value {{ color: #FFFFFF; }}
  .kpi.primary .icon {{ background: rgba(255,255,255,.1); }}

  .insight {{ background: {PAPER}; border-left: 4px solid {AMBER}; border-radius: 10px;
              padding: 14px 18px; height: 100%; }}
  .insight .head {{ color: {NAVY}; font-weight: 700; margin-bottom: 4px; }}
  .insight .body {{ color: {INK}; font-size: .93rem; }}

  .section-label {{ color: {MUTED}; font-size: .78rem; font-weight: 700;
                    letter-spacing: .12em; text-transform: uppercase; margin: 32px 0 10px; }}
  .footnote {{ color: {MUTED}; font-size: .82rem; border-top: 1px solid {LINE};
              padding-top: 14px; margin-top: 36px; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Illustrations (inline SVG, drawn in the brand palette)
# ---------------------------------------------------------------
HERO_ART = f"""
<svg width="230" height="150" viewBox="0 0 230 150" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="120" cy="138" rx="100" ry="8" fill="#000" opacity=".18"/>
  <!-- house -->
  <rect x="40" y="62" width="96" height="74" rx="4" fill="#FFFFFF"/>
  <path d="M30 68 L88 22 L146 68 Z" fill="{AMBER}"/>
  <rect x="112" y="30" width="12" height="24" fill="#FFFFFF"/>
  <rect x="76" y="96" width="24" height="40" rx="3" fill="{NAVY}"/>
  <circle cx="95" cy="117" r="2" fill="{AMBER}"/>
  <rect x="50" y="78" width="18" height="16" rx="2" fill="{SKY}"/>
  <rect x="108" y="78" width="18" height="16" rx="2" fill="{SKY}"/>
  <!-- coin stack -->
  <g>
    <ellipse cx="180" cy="130" rx="22" ry="7" fill="#B7791F"/>
    <rect x="158" y="116" width="44" height="14" fill="{AMBER}"/>
    <ellipse cx="180" cy="116" rx="22" ry="7" fill="#F3C677"/>
    <rect x="158" y="102" width="44" height="14" fill="{AMBER}"/>
    <ellipse cx="180" cy="102" rx="22" ry="7" fill="#F3C677"/>
    <rect x="158" y="88" width="44" height="14" fill="{AMBER}"/>
    <ellipse cx="180" cy="88" rx="22" ry="7" fill="#F3C677"/>
    <text x="180" y="92" text-anchor="middle" font-family="Georgia, serif" font-size="11"
          font-weight="700" fill="#8A5A12">$</text>
  </g>
  <!-- falling-balance arrow -->
  <path d="M160 26 Q190 34 205 66" stroke="#FFFFFF" stroke-width="3" fill="none"
        stroke-linecap="round" stroke-dasharray="1 7"/>
  <path d="M198 62 L206 70 L210 59" stroke="#FFFFFF" stroke-width="3" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

ICONS = {
    "repayment": f"""<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF"
        stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>
        <circle cx="12" cy="15.5" r="1.6" fill="#FFFFFF"/></svg>""",
    "interest": f"""<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="{AMBER}"
        stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 19L19 5"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/></svg>""",
    "total": f"""<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="{NAVY}"
        stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>
        <path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/></svg>""",
    "ratio": f"""<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="{NAVY}"
        stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>""",
}


def kpi(col, icon, label, value, primary=False):
    col.markdown(f"""
      <div class="kpi {'primary' if primary else ''}">
        <div class="icon">{ICONS[icon]}</div>
        <div><div class="label">{label}</div><div class="value">{value}</div></div>
      </div>""", unsafe_allow_html=True)


def insight(col, head, body):
    col.markdown(f"""
      <div class="insight"><div class="head">{head}</div><div class="body">{body}</div></div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <div>
    <p class="eyebrow">Financial Planning Tool</p>
    <h1>Loan Repayment Calculator</h1>
    <p>Estimate your repayments, see the true cost of borrowing, and understand how every
       payment is split between interest and the loan itself.</p>
  </div>
  {HERO_ART}
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### Loan details")
    principal = st.number_input("Loan amount (AUD)", min_value=1_000, max_value=10_000_000,
                                value=500_000, step=10_000)
    rate = st.number_input("Interest rate (% p.a.)", min_value=0.0, max_value=30.0,
                           value=6.0, step=0.05, format="%.2f")
    years = st.slider("Loan term (years)", min_value=1, max_value=40, value=30)
    frequency = st.selectbox("Repayment frequency", ["Monthly", "Fortnightly", "Weekly"])
    st.caption("Assumes a fixed rate for the full term, with no fees or extra repayments.")

freq = {"Monthly": 12, "Fortnightly": 26, "Weekly": 52}[frequency]


# ---------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------
summary = loan_summary(principal, rate, years, freq)
table = schedule(principal, rate, years, freq)

table["year"] = (table["period"] - 1) // freq + 1
yearly = table.groupby("year").agg(
    payments=("payment", "sum"),
    interest=("interest", "sum"),
    principal=("principal", "sum"),
    closing_balance=("balance", "last"),
)
yearly["closing_balance"] = yearly["closing_balance"].clip(lower=0)

cost_per_dollar = summary["total_paid"] / principal


# ---------------------------------------------------------------
# Headline figures
# ---------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
kpi(c1, "repayment", f"{frequency} repayment", f"${summary['repayment']:,.2f}", primary=True)
kpi(c2, "interest", "Total interest", f"${summary['total_interest']:,.0f}")
kpi(c3, "total", "Total repaid", f"${summary['total_paid']:,.0f}")
kpi(c4, "ratio", "Repaid per $1 borrowed", f"${cost_per_dollar:,.2f}")


# ---------------------------------------------------------------
# Key insights
# ---------------------------------------------------------------
st.markdown('<div class="section-label">Key insights</div>', unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)

# 1. Share of repayments that is interest
interest_share = summary["total_interest"] / summary["total_paid"] if summary["total_paid"] else 0
insight(i1, "The cost of borrowing",
        f"Interest makes up <b>{interest_share:.0%}</b> of everything you repay. "
        f"For every $1 borrowed, you pay back <b>${cost_per_dollar:,.2f}</b>.")

# 2. Turning point: when principal first exceeds interest
turning = table[table["principal"] > table["interest"]]
if rate == 0:
    insight(i2, "The turning point", "With no interest, every dollar you repay reduces the loan.")
elif turning.empty:
    insight(i2, "The turning point", "Interest exceeds principal in every repayment of this loan.")
elif turning["period"].iloc[0] == 1:
    insight(i2, "The turning point",
            "From your very first repayment, most of each payment goes towards the loan itself.")
else:
    turn_year = int(turning["year"].iloc[0])
    insight(i2, "The turning point",
            f"Most of each repayment goes to interest until <b>year {turn_year}</b>. "
            f"After that, the majority starts paying down the loan.")

# 3. What a shorter term would save
if years > 5:
    shorter = loan_summary(principal, rate, years - 5, freq)
    extra = shorter["repayment"] - summary["repayment"]
    saved = summary["total_interest"] - shorter["total_interest"]
    insight(i3, f"Repay in {years - 5} years instead",
            f"Paying <b>${extra:,.2f}</b> more per {frequency.lower().replace('ly', '')} "
            f"would save <b>${saved:,.0f}</b> in interest.")
else:
    insight(i3, "Short-term loan",
            "On a term this short, most of the cost is the loan itself rather than interest.")


# ---------------------------------------------------------------
# Charts
# ---------------------------------------------------------------
st.markdown('<div class="section-label">How the loan is repaid</div>', unsafe_allow_html=True)
left, right = st.columns(2)

balance_df = pd.DataFrame({
    "Year": [0] + list(yearly.index),
    "Balance": [principal] + list(yearly["closing_balance"]),
})
balance_chart = (
    alt.Chart(balance_df, title="Outstanding balance")
    .mark_area(line={"color": NAVY, "strokeWidth": 2.5}, color=alt.Gradient(
        gradient="linear", x1=1, x2=1, y1=1, y2=0,
        stops=[alt.GradientStop(color="#FFFFFF", offset=0),
               alt.GradientStop(color=SKY, offset=1)]))
    .encode(
        x=alt.X("Year:Q", axis=alt.Axis(tickMinStep=1, grid=False)),
        y=alt.Y("Balance:Q", axis=alt.Axis(format="$,.0s", title=None)),
        tooltip=[alt.Tooltip("Year:Q"), alt.Tooltip("Balance:Q", format="$,.0f")],
    )
    .properties(height=320)
)
left.altair_chart(balance_chart, width="stretch")

split_df = (
    yearly[["principal", "interest"]]
    .rename(columns={"principal": "Principal", "interest": "Interest"})
    .reset_index()
    .melt(id_vars="year", var_name="Component", value_name="Amount")
)
split_chart = (
    alt.Chart(split_df, title="Where each year's repayments go")
    .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
    .encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, values=list(
            range(1, years + 1, max(1, years // 10))))),
        y=alt.Y("Amount:Q", axis=alt.Axis(format="$,.0s", title=None)),
        color=alt.Color("Component:N",
                        scale=alt.Scale(domain=["Interest", "Principal"], range=[AMBER, NAVY]),
                        legend=alt.Legend(orient="top", title=None)),
        order=alt.Order("Component:N", sort="descending"),
        tooltip=["year:O", "Component:N", alt.Tooltip("Amount:Q", format="$,.0f")],
    )
    .properties(height=320)
)
right.altair_chart(split_chart, width="stretch")


# ---------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------
st.markdown('<div class="section-label">Amortisation schedule</div>', unsafe_allow_html=True)

money = st.column_config.NumberColumn(format="dollar")
st.dataframe(
    yearly.reset_index().rename(columns={
        "year": "Year", "payments": "Repayments", "interest": "Interest",
        "principal": "Principal", "closing_balance": "Closing balance",
    }),
    hide_index=True,
    column_config={
        "Year": st.column_config.NumberColumn(format="%d"),
        "Repayments": money, "Interest": money,
        "Principal": money, "Closing balance": money,
    },
)

export = table.drop(columns="year").round(2)
export.columns = ["Period", "Repayment", "Interest", "Principal", "Balance"]
st.download_button("Download full schedule (CSV)", data=export.to_csv(index=False),
                   file_name="amortisation_schedule.csv", mime="text/csv", type="primary")

