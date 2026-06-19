-- ============================================================
--         SALES ANALYSIS SQL PROJECT
--         By: Priyanshu | Data Analyst Internship Portfolio
-- ============================================================
-- Dataset: 50,000 orders | 6 categories | 4 regions | 5 payment methods
-- Tools: SQL (PostgreSQL / MySQL compatible)
-- ============================================================


-- ============================================================
-- SECTION 1: TABLE SETUP
-- ============================================================

CREATE TABLE IF NOT EXISTS sales_analysis (
    order_id          INT PRIMARY KEY,
    order_date        DATE,
    product_id        INT,
    product_category  VARCHAR(50),
    price             DECIMAL(10, 2),
    discount_percent  INT,
    quantity_sold     INT,
    customer_region   VARCHAR(50),
    payment_method    VARCHAR(50),
    rating            DECIMAL(3, 1),
    review_count      INT,
    discounted_price  DECIMAL(10, 2),
    total_revenue     DECIMAL(10, 2)
);

-- ============================================================
-- SECTION 2: DATABASE EXPLORATION (Always start with this!)
-- ============================================================

-- Q1: How many total orders are in the dataset?
SELECT COUNT(*) AS total_orders
FROM sales_analysis;

-- Q2: Preview the first 10 records
SELECT *
FROM sales_analysis
LIMIT 10;

-- Q3: Check date range of orders
SELECT
    MIN(order_date) AS earliest_order,
    MAX(order_date) AS latest_order,
    COUNT(DISTINCT YEAR(order_date)) AS total_years
FROM sales_analysis;

-- Q4: Check for NULL values in critical columns
SELECT
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END)         AS null_order_id,
    SUM(CASE WHEN total_revenue IS NULL THEN 1 ELSE 0 END)    AS null_revenue,
    SUM(CASE WHEN customer_region IS NULL THEN 1 ELSE 0 END)  AS null_region,
    SUM(CASE WHEN payment_method IS NULL THEN 1 ELSE 0 END)   AS null_payment
FROM sales_analysis;


-- ============================================================
-- SECTION 3: REVENUE & SALES ANALYSIS
-- ============================================================

-- Q5: What is the total revenue generated across all orders?
SELECT
    ROUND(SUM(total_revenue), 2)  AS total_revenue,
    ROUND(AVG(total_revenue), 2)  AS avg_order_revenue,
    ROUND(MIN(total_revenue), 2)  AS min_order_revenue,
    ROUND(MAX(total_revenue), 2)  AS max_order_revenue
FROM sales_analysis;

-- Q6: Total revenue and orders by product category
SELECT
    product_category,
    COUNT(order_id)                        AS total_orders,
    SUM(quantity_sold)                     AS total_units_sold,
    ROUND(SUM(total_revenue), 2)           AS total_revenue,
    ROUND(AVG(total_revenue), 2)           AS avg_revenue_per_order,
    ROUND(SUM(total_revenue) * 100.0 /
          SUM(SUM(total_revenue)) OVER (), 2) AS revenue_share_pct
FROM sales_analysis
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Q7: Revenue by customer region
SELECT
    customer_region,
    COUNT(order_id)               AS total_orders,
    ROUND(SUM(total_revenue), 2)  AS total_revenue,
    ROUND(AVG(rating), 2)         AS avg_rating
FROM sales_analysis
GROUP BY customer_region
ORDER BY total_revenue DESC;

-- Q8: Which payment method is most popular and generates the most revenue?
SELECT
    payment_method,
    COUNT(order_id)               AS total_orders,
    ROUND(SUM(total_revenue), 2)  AS total_revenue,
    ROUND(AVG(discount_percent), 1) AS avg_discount_pct
FROM sales_analysis
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ============================================================
-- SECTION 4: DISCOUNT IMPACT ANALYSIS
-- ============================================================

-- Q9: How does discount percentage impact revenue and quantity sold?
SELECT
    discount_percent,
    COUNT(order_id)                AS total_orders,
    ROUND(AVG(quantity_sold), 2)   AS avg_quantity_sold,
    ROUND(AVG(total_revenue), 2)   AS avg_revenue,
    ROUND(AVG(rating), 2)          AS avg_rating
FROM sales_analysis
GROUP BY discount_percent
ORDER BY discount_percent;

-- Q10: Classify orders by discount tier and compare performance
SELECT
    CASE
        WHEN discount_percent = 0          THEN 'No Discount'
        WHEN discount_percent BETWEEN 1 AND 10  THEN 'Low (1-10%)'
        WHEN discount_percent BETWEEN 11 AND 20 THEN 'Medium (11-20%)'
        WHEN discount_percent BETWEEN 21 AND 30 THEN 'High (21-30%)'
        ELSE 'Very High (>30%)'
    END AS discount_tier,
    COUNT(order_id)                AS total_orders,
    ROUND(AVG(total_revenue), 2)   AS avg_revenue,
    ROUND(AVG(quantity_sold), 2)   AS avg_qty_sold,
    ROUND(AVG(rating), 2)          AS avg_customer_rating
FROM sales_analysis
GROUP BY discount_tier
ORDER BY avg_revenue DESC;

-- Q11: Revenue lost to discounts vs. potential revenue (at full price)
SELECT
    product_category,
    ROUND(SUM(price * quantity_sold), 2)        AS revenue_at_full_price,
    ROUND(SUM(total_revenue), 2)                AS actual_revenue,
    ROUND(SUM(price * quantity_sold)
          - SUM(total_revenue), 2)              AS revenue_lost_to_discounts,
    ROUND((SUM(price * quantity_sold)
          - SUM(total_revenue)) * 100.0
          / SUM(price * quantity_sold), 2)      AS discount_loss_pct
FROM sales_analysis
GROUP BY product_category
ORDER BY revenue_lost_to_discounts DESC;


-- ============================================================
-- SECTION 5: TIME-BASED TREND ANALYSIS
-- ============================================================

-- Q12: Monthly revenue trend
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS year_month,
    COUNT(order_id)                   AS total_orders,
    ROUND(SUM(total_revenue), 2)      AS monthly_revenue
FROM sales_analysis
GROUP BY year_month
ORDER BY year_month;

-- Q13: Year-over-Year revenue comparison
SELECT
    YEAR(order_date)              AS order_year,
    COUNT(order_id)               AS total_orders,
    ROUND(SUM(total_revenue), 2)  AS yearly_revenue,
    ROUND(AVG(rating), 2)         AS avg_rating
FROM sales_analysis
GROUP BY order_year
ORDER BY order_year;

-- Q14: Which month performs best on average? (Seasonality check)
SELECT
    MONTH(order_date)             AS month_num,
    MONTHNAME(order_date)         AS month_name,
    ROUND(AVG(total_revenue), 2)  AS avg_monthly_revenue,
    COUNT(order_id)               AS total_orders
FROM sales_analysis
GROUP BY month_num, month_name
ORDER BY avg_monthly_revenue DESC;

-- Q15: Day of week analysis — which day sees the most orders?
SELECT
    DAYNAME(order_date)       AS day_of_week,
    COUNT(order_id)           AS total_orders,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM sales_analysis
GROUP BY day_of_week
ORDER BY total_orders DESC;


-- ============================================================
-- SECTION 6: CUSTOMER & RATING ANALYSIS
-- ============================================================

-- Q16: Rating distribution across the dataset
SELECT
    rating,
    COUNT(order_id)               AS total_orders,
    ROUND(SUM(total_revenue), 2)  AS total_revenue
FROM sales_analysis
GROUP BY rating
ORDER BY rating DESC;

-- Q17: Average rating by category — which category delights customers most?
SELECT
    product_category,
    ROUND(AVG(rating), 2)       AS avg_rating,
    COUNT(order_id)             AS total_orders,
    SUM(review_count)           AS total_reviews
FROM sales_analysis
GROUP BY product_category
ORDER BY avg_rating DESC;

-- Q18: High-revenue but low-rated orders (potential problem products)
SELECT
    order_id,
    product_category,
    total_revenue,
    rating,
    customer_region
FROM sales_analysis
WHERE rating <= 2.5
  AND total_revenue > (SELECT AVG(total_revenue) FROM sales_analysis)
ORDER BY total_revenue DESC
LIMIT 20;


-- ============================================================
-- SECTION 7: ADVANCED SQL — CTEs, WINDOW FUNCTIONS, SUBQUERIES
-- ============================================================

-- Q19: Running total revenue over time (Window Function)
SELECT
    order_date,
    order_id,
    total_revenue,
    ROUND(SUM(total_revenue) OVER (ORDER BY order_date, order_id), 2) AS running_total_revenue
FROM sales_analysis
ORDER BY order_date, order_id
LIMIT 100;

-- Q20: Rank product categories by revenue within each region (Window Function)
SELECT
    customer_region,
    product_category,
    ROUND(SUM(total_revenue), 2) AS category_revenue,
    RANK() OVER (
        PARTITION BY customer_region
        ORDER BY SUM(total_revenue) DESC
    ) AS revenue_rank
FROM sales_analysis
GROUP BY customer_region, product_category
ORDER BY customer_region, revenue_rank;

-- Q21: Month-over-Month revenue growth using CTE + LAG
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m')  AS year_month,
        ROUND(SUM(total_revenue), 2)       AS revenue
    FROM sales_analysis
    GROUP BY year_month
)
SELECT
    year_month,
    revenue,
    LAG(revenue) OVER (ORDER BY year_month)                  AS prev_month_revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY year_month), 2) AS mom_change,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY year_month)) * 100.0
          / LAG(revenue) OVER (ORDER BY year_month), 2)      AS mom_growth_pct
FROM monthly_revenue
ORDER BY year_month;

-- Q22: Top 10% revenue orders using NTILE (Window Function)
WITH order_tiles AS (
    SELECT
        order_id,
        product_category,
        customer_region,
        total_revenue,
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile
    FROM sales_analysis
)
SELECT *
FROM order_tiles
WHERE revenue_decile = 1
ORDER BY total_revenue DESC
LIMIT 20;

-- Q23: Category performance vs. overall average (CTE + Subquery)
WITH category_stats AS (
    SELECT
        product_category,
        ROUND(AVG(total_revenue), 2) AS avg_category_revenue,
        ROUND(AVG(rating), 2)        AS avg_category_rating
    FROM sales_analysis
    GROUP BY product_category
),
overall AS (
    SELECT
        ROUND(AVG(total_revenue), 2) AS overall_avg_revenue,
        ROUND(AVG(rating), 2)        AS overall_avg_rating
    FROM sales_analysis
)
SELECT
    c.product_category,
    c.avg_category_revenue,
    o.overall_avg_revenue,
    ROUND(c.avg_category_revenue - o.overall_avg_revenue, 2) AS revenue_vs_avg,
    c.avg_category_rating,
    o.overall_avg_rating,
    ROUND(c.avg_category_rating - o.overall_avg_rating, 2)   AS rating_vs_avg,
    CASE
        WHEN c.avg_category_revenue > o.overall_avg_revenue
         AND c.avg_category_rating  > o.overall_avg_rating  THEN 'Star Performer'
        WHEN c.avg_category_revenue > o.overall_avg_revenue
         AND c.avg_category_rating <= o.overall_avg_rating  THEN 'High Revenue, Low Satisfaction'
        WHEN c.avg_category_revenue <= o.overall_avg_revenue
         AND c.avg_category_rating  > o.overall_avg_rating  THEN 'Low Revenue, High Satisfaction'
        ELSE 'Needs Improvement'
    END AS performance_label
FROM category_stats c
CROSS JOIN overall o
ORDER BY c.avg_category_revenue DESC;

-- Q24: Identify orders with above-average revenue within their own category
SELECT
    order_id,
    product_category,
    total_revenue,
    ROUND(AVG(total_revenue) OVER (PARTITION BY product_category), 2) AS category_avg_revenue,
    ROUND(total_revenue - AVG(total_revenue) OVER (PARTITION BY product_category), 2) AS diff_from_avg
FROM sales_analysis
WHERE total_revenue > (
    SELECT AVG(s2.total_revenue)
    FROM sales_analysis s2
    WHERE s2.product_category = sales_analysis.product_category
)
ORDER BY diff_from_avg DESC
LIMIT 20;


-- ============================================================
-- SECTION 8: BUSINESS INSIGHTS QUERIES
-- ============================================================

-- Q25: Region x Category revenue heatmap (Pivot-style)
SELECT
    customer_region,
    ROUND(SUM(CASE WHEN product_category = 'Electronics'    THEN total_revenue ELSE 0 END), 2) AS Electronics,
    ROUND(SUM(CASE WHEN product_category = 'Fashion'        THEN total_revenue ELSE 0 END), 2) AS Fashion,
    ROUND(SUM(CASE WHEN product_category = 'Books'          THEN total_revenue ELSE 0 END), 2) AS Books,
    ROUND(SUM(CASE WHEN product_category = 'Beauty'         THEN total_revenue ELSE 0 END), 2) AS Beauty,
    ROUND(SUM(CASE WHEN product_category = 'Sports'         THEN total_revenue ELSE 0 END), 2) AS Sports,
    ROUND(SUM(CASE WHEN product_category = 'Home & Kitchen' THEN total_revenue ELSE 0 END), 2) AS Home_Kitchen
FROM sales_analysis
GROUP BY customer_region
ORDER BY customer_region;

-- Q26: Payment method preference by region
SELECT
    customer_region,
    payment_method,
    COUNT(order_id) AS total_orders,
    ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER (PARTITION BY customer_region), 2) AS pct_in_region
FROM sales_analysis
GROUP BY customer_region, payment_method
ORDER BY customer_region, total_orders DESC;

-- Q27: High-volume, high-discount orders — are discounts driving bulk purchases?
SELECT
    discount_percent,
    ROUND(AVG(quantity_sold), 2)   AS avg_qty,
    ROUND(AVG(total_revenue), 2)   AS avg_revenue,
    COUNT(order_id)                AS total_orders
FROM sales_analysis
WHERE quantity_sold > (SELECT AVG(quantity_sold) FROM sales_analysis)
GROUP BY discount_percent
ORDER BY discount_percent;

-- Q28: Top 5 performing products by total revenue
SELECT
    product_id,
    product_category,
    COUNT(order_id)                AS total_orders,
    ROUND(SUM(total_revenue), 2)   AS total_revenue,
    ROUND(AVG(rating), 2)          AS avg_rating
FROM sales_analysis
GROUP BY product_id, product_category
ORDER BY total_revenue DESC
LIMIT 5;

-- Q29: Complete KPI summary dashboard (one-shot executive report)
SELECT
    COUNT(order_id)                                AS total_orders,
    ROUND(SUM(total_revenue), 2)                  AS total_revenue,
    ROUND(AVG(total_revenue), 2)                  AS avg_order_value,
    ROUND(AVG(rating), 2)                         AS avg_customer_rating,
    ROUND(AVG(discount_percent), 1)               AS avg_discount_pct,
    SUM(quantity_sold)                            AS total_units_sold,
    COUNT(DISTINCT product_category)              AS product_categories,
    COUNT(DISTINCT customer_region)               AS regions_served,
    COUNT(DISTINCT payment_method)                AS payment_methods
FROM sales_analysis;


-- ============================================================
-- END OF PROJECT
-- ============================================================