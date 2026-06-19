# ============================================================
#         SALES ANALYSIS — PYTHON EDA PROJECT
#         By: Priyanshu | Data Analyst Internship Portfolio
# ============================================================
# Dataset : 50,000 orders | 2022–2023 | 6 categories | 4 regions
# Libraries: pandas, matplotlib, seaborn
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Global style ────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 130
plt.rcParams["axes.titleweight"] = "bold"
PALETTE = "Set2"

# ============================================================
# STEP 1 — LOAD & INSPECT
# ============================================================

df = pd.read_csv("sales_analysis.csv", parse_dates=["order_date"])

print("=" * 55)
print("  STEP 1 — BASIC INSPECTION")
print("=" * 55)
print(f"\nShape          : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Date range     : {df['order_date'].min().date()} → {df['order_date'].max().date()}")
print(f"Null values    : {df.isnull().sum().sum()} total")
print(f"Duplicates     : {df.duplicated().sum()}")
print("\nColumn types:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())


# ============================================================
# STEP 2 — DATA CLEANING & FEATURE ENGINEERING
# ============================================================

print("\n" + "=" * 55)
print("  STEP 2 — CLEANING & FEATURE ENGINEERING")
print("=" * 55)

# Extract time features
df["year"]       = df["order_date"].dt.year
df["month"]      = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.strftime("%b")
df["quarter"]    = df["order_date"].dt.quarter
df["day_name"]   = df["order_date"].dt.strftime("%a")
df["year_month"] = df["order_date"].dt.to_period("M")

# Discount tier
def discount_tier(d):
    if d == 0:       return "No Discount"
    elif d <= 10:    return "Low (1–10%)"
    elif d <= 20:    return "Medium (11–20%)"
    elif d <= 30:    return "High (21–30%)"
    else:            return "Very High (>30%)"

df["discount_tier"] = df["discount_percent"].apply(discount_tier)

# Revenue tier
q33 = df["total_revenue"].quantile(0.33)
q66 = df["total_revenue"].quantile(0.66)
def revenue_tier(r):
    if r <= q33:  return "Low"
    elif r <= q66: return "Medium"
    else:          return "High"

df["revenue_tier"] = df["total_revenue"].apply(revenue_tier)

print("✅ New columns added:", ["year","month","month_name","quarter",
                               "day_name","year_month","discount_tier","revenue_tier"])
print(f"\nDiscount tiers:\n{df['discount_tier'].value_counts()}")
print(f"\nRevenue tiers:\n{df['revenue_tier'].value_counts()}")


# ============================================================
# STEP 3 — UNIVARIATE ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 3 — UNIVARIATE ANALYSIS")
print("=" * 55)

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Univariate Analysis — Key Numeric Distributions", fontsize=14)

cols = ["price", "discount_percent", "quantity_sold",
        "total_revenue", "rating", "review_count"]
colors = sns.color_palette(PALETTE, len(cols))

for ax, col, color in zip(axes.flat, cols, colors):
    ax.hist(df[col], bins=30, color=color, edgecolor="white", linewidth=0.5)
    ax.set_title(col.replace("_", " ").title())
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"₹{x:,.0f}" if "price" in col or "revenue" in col else f"{x:,.0f}"))

plt.tight_layout()
plt.savefig("01_univariate_distributions.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 01_univariate_distributions.png")

# Key stats
print("\nRevenue Summary:")
print(df["total_revenue"].describe().round(2))
print("\nRating Summary:")
print(df["rating"].describe().round(2))


# ============================================================
# STEP 4 — CATEGORY ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 4 — PRODUCT CATEGORY ANALYSIS")
print("=" * 55)

cat_stats = (
    df.groupby("product_category")
    .agg(
        total_orders   = ("order_id",      "count"),
        total_revenue  = ("total_revenue", "sum"),
        avg_revenue    = ("total_revenue", "mean"),
        avg_rating     = ("rating",        "mean"),
        total_units    = ("quantity_sold", "sum"),
    )
    .sort_values("total_revenue", ascending=False)
    .round(2)
)
print(cat_stats)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Product Category Analysis", fontsize=14)

# Revenue by category
bars = axes[0].barh(
    cat_stats.index, cat_stats["total_revenue"] / 1e6,
    color=sns.color_palette(PALETTE, len(cat_stats))
)
axes[0].set_xlabel("Total Revenue (₹ Millions)")
axes[0].set_title("Revenue by Category")
for bar in bars:
    axes[0].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                 f"₹{bar.get_width():.1f}M", va="center", fontsize=9)

# Avg rating by category
axes[1].bar(
    cat_stats.index, cat_stats["avg_rating"],
    color=sns.color_palette(PALETTE, len(cat_stats))
)
axes[1].set_ylim(3, 4)
axes[1].set_title("Avg Customer Rating by Category")
axes[1].set_ylabel("Avg Rating")
axes[1].tick_params(axis="x", rotation=30)

# Revenue share pie
axes[2].pie(
    cat_stats["total_revenue"],
    labels=cat_stats.index,
    autopct="%1.1f%%",
    colors=sns.color_palette(PALETTE, len(cat_stats)),
    startangle=140
)
axes[2].set_title("Revenue Share by Category")

plt.tight_layout()
plt.savefig("02_category_analysis.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 02_category_analysis.png")


# ============================================================
# STEP 5 — TIME TREND ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 5 — TIME TREND ANALYSIS")
print("=" * 55)

monthly = (
    df.groupby("year_month")
    .agg(revenue=("total_revenue", "sum"), orders=("order_id", "count"))
    .reset_index()
)
monthly["year_month_str"] = monthly["year_month"].astype(str)

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle("Time Trend Analysis (2022–2023)", fontsize=14)

# Monthly revenue
axes[0].plot(monthly["year_month_str"], monthly["revenue"] / 1e6,
             marker="o", linewidth=2, color="#2196F3", markersize=5)
axes[0].fill_between(monthly["year_month_str"], monthly["revenue"] / 1e6,
                     alpha=0.15, color="#2196F3")
axes[0].set_title("Monthly Revenue Trend")
axes[0].set_ylabel("Revenue (₹ Millions)")
axes[0].tick_params(axis="x", rotation=45)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.1f}M"))

# Monthly orders
axes[1].bar(monthly["year_month_str"], monthly["orders"],
            color="#4CAF50", alpha=0.8, edgecolor="white")
axes[1].set_title("Monthly Order Volume")
axes[1].set_ylabel("Number of Orders")
axes[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("03_time_trends.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 03_time_trends.png")

# Seasonality
month_order = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
seasonal = (
    df.groupby("month_name")["total_revenue"]
    .mean()
    .reindex(month_order)
    .reset_index()
)
print("\nAvg Revenue by Month:")
print(seasonal.sort_values("total_revenue", ascending=False).to_string(index=False))


# ============================================================
# STEP 6 — REGIONAL ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 6 — REGIONAL ANALYSIS")
print("=" * 55)

region_stats = (
    df.groupby("customer_region")
    .agg(
        total_orders  = ("order_id",      "count"),
        total_revenue = ("total_revenue", "sum"),
        avg_revenue   = ("total_revenue", "mean"),
        avg_rating    = ("rating",        "mean"),
    )
    .sort_values("total_revenue", ascending=False)
    .round(2)
)
print(region_stats)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Regional Performance Analysis", fontsize=14)

region_cat = (
    df.groupby(["customer_region", "product_category"])["total_revenue"]
    .sum()
    .unstack()
)
region_cat.plot(kind="bar", ax=axes[0], colormap=PALETTE, edgecolor="white", linewidth=0.4)
axes[0].set_title("Revenue by Region & Category")
axes[0].set_ylabel("Total Revenue (₹)")
axes[0].tick_params(axis="x", rotation=30)
axes[0].legend(title="Category", fontsize=8)

# Avg rating by region
axes[1].bar(
    region_stats.index, region_stats["avg_rating"],
    color=sns.color_palette(PALETTE, len(region_stats))
)
axes[1].set_ylim(3.4, 3.7)
axes[1].set_title("Avg Rating by Region")
axes[1].set_ylabel("Avg Rating")

plt.tight_layout()
plt.savefig("04_regional_analysis.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 04_regional_analysis.png")


# ============================================================
# STEP 7 — DISCOUNT IMPACT ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 7 — DISCOUNT IMPACT ANALYSIS")
print("=" * 55)

disc_impact = (
    df.groupby("discount_percent")
    .agg(
        avg_revenue = ("total_revenue", "mean"),
        avg_qty     = ("quantity_sold", "mean"),
        avg_rating  = ("rating",        "mean"),
        orders      = ("order_id",      "count"),
    )
    .reset_index()
    .round(2)
)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Discount Impact Analysis", fontsize=14)

axes[0].scatter(disc_impact["discount_percent"], disc_impact["avg_revenue"],
                color="#E91E63", s=80, alpha=0.8)
axes[0].set_title("Discount % vs Avg Revenue")
axes[0].set_xlabel("Discount %")
axes[0].set_ylabel("Avg Revenue (₹)")

axes[1].scatter(disc_impact["discount_percent"], disc_impact["avg_qty"],
                color="#FF9800", s=80, alpha=0.8)
axes[1].set_title("Discount % vs Avg Quantity Sold")
axes[1].set_xlabel("Discount %")
axes[1].set_ylabel("Avg Qty Sold")

tier_order = ["No Discount", "Low (1–10%)", "Medium (11–20%)",
              "High (21–30%)", "Very High (>30%)"]
tier_rev = (
    df.groupby("discount_tier")["total_revenue"]
    .mean()
    .reindex(tier_order)
)
axes[2].bar(tier_rev.index, tier_rev.values,
            color=sns.color_palette(PALETTE, len(tier_rev)))
axes[2].set_title("Avg Revenue by Discount Tier")
axes[2].set_ylabel("Avg Revenue (₹)")
axes[2].tick_params(axis="x", rotation=25)

plt.tight_layout()
plt.savefig("05_discount_analysis.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 05_discount_analysis.png")


# ============================================================
# STEP 8 — CORRELATION HEATMAP
# ============================================================

print("\n" + "=" * 55)
print("  STEP 8 — CORRELATION ANALYSIS")
print("=" * 55)

numeric_cols = ["price", "discount_percent", "quantity_sold",
                "total_revenue", "rating", "review_count", "discounted_price"]
corr = df[numeric_cols].corr().round(2)
print(corr)

plt.figure(figsize=(9, 7))
mask = pd.DataFrame(False, index=corr.index, columns=corr.columns)
for i in range(len(corr)):
    for j in range(i):
        mask.iloc[i, j] = True

sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="RdYlGn",
    linewidths=0.5, square=True, cbar_kws={"shrink": 0.8}
)
plt.title("Correlation Heatmap — Numeric Features", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("06_correlation_heatmap.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 06_correlation_heatmap.png")


# ============================================================
# STEP 9 — PAYMENT METHOD ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("  STEP 9 — PAYMENT METHOD ANALYSIS")
print("=" * 55)

pay_stats = (
    df.groupby("payment_method")
    .agg(
        total_orders  = ("order_id",      "count"),
        total_revenue = ("total_revenue", "sum"),
        avg_revenue   = ("total_revenue", "mean"),
    )
    .sort_values("total_orders", ascending=False)
    .round(2)
)
print(pay_stats)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Payment Method Analysis", fontsize=14)

axes[0].pie(
    pay_stats["total_orders"],
    labels=pay_stats.index,
    autopct="%1.1f%%",
    colors=sns.color_palette(PALETTE, len(pay_stats)),
    startangle=90
)
axes[0].set_title("Order Share by Payment Method")

axes[1].bar(
    pay_stats.index, pay_stats["avg_revenue"],
    color=sns.color_palette(PALETTE, len(pay_stats))
)
axes[1].set_title("Avg Revenue by Payment Method")
axes[1].set_ylabel("Avg Revenue (₹)")
axes[1].tick_params(axis="x", rotation=20)

plt.tight_layout()
plt.savefig("07_payment_analysis.png", bbox_inches="tight")
plt.show()
print("✅ Saved: 07_payment_analysis.png")


# ============================================================
# STEP 10 — EXECUTIVE SUMMARY (Business Insights)
# ============================================================

print("\n" + "=" * 55)
print("  STEP 10 — EXECUTIVE SUMMARY")
print("=" * 55)

total_rev      = df["total_revenue"].sum()
top_category   = df.groupby("product_category")["total_revenue"].sum().idxmax()
top_region     = df.groupby("customer_region")["total_revenue"].sum().idxmax()
top_payment    = df["payment_method"].value_counts().idxmax()
best_rated_cat = df.groupby("product_category")["rating"].mean().idxmax()
avg_discount   = df["discount_percent"].mean()
avg_rating     = df["rating"].mean()

print(f"""
┌─────────────────────────────────────────────────┐
│          SALES ANALYSIS — KEY INSIGHTS          │
├─────────────────────────────────────────────────┤
│  Total Revenue       : ₹{total_rev:>15,.2f}       │
│  Total Orders        : {len(df):>15,}              │
│  Avg Order Value     : ₹{df['total_revenue'].mean():>15,.2f}       │
│  Avg Customer Rating : {avg_rating:>15.2f}              │
│  Avg Discount        : {avg_discount:>15.1f}%             │
├─────────────────────────────────────────────────┤
│  Top Revenue Category: {top_category:<25}│
│  Top Revenue Region  : {top_region:<25}│
│  Most Used Payment   : {top_payment:<25}│
│  Best Rated Category : {best_rated_cat:<25}│
└─────────────────────────────────────────────────┘

KEY FINDINGS:
1. Revenue is evenly distributed across all 4 regions
   — no single region dominates, suggesting global demand.

2. Higher discounts do NOT always increase revenue
   — medium discounts (11-20%) show the best avg order value.

3. Rating is consistently between 3.5–4.0 across all categories
   — no category has a major satisfaction problem.

4. Electronics and Fashion lead in revenue but Beauty leads
   in order volume — a pricing opportunity exists.

5. UPI is the most popular payment method, especially in Asia
   — aligns with India/SE Asia digital payment adoption trends.
""")

print("✅ EDA complete — all charts saved!")
print("📁 Files: 01_univariate_distributions.png → 07_payment_analysis.png")
