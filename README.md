<div align="center">
  
# 🛒 Dominick's Fine Foods (DFF) Data Warehouse
**An End-to-End Enterprise Data Warehousing & Business Intelligence Project**

[![SQL Server](https://img.shields.io/badge/SQL%20Server-CC292B?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/en-us/sql-server)
[![SSIS](https://img.shields.io/badge/SSIS-0078D7?style=for-the-badge&logo=microsoft&logoColor=white)](https://docs.microsoft.com/en-us/sql/integration-services)
[![SSAS](https://img.shields.io/badge/SSAS-861B2D?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)](https://docs.microsoft.com/en-us/analysis-services)
[![SSRS](https://img.shields.io/badge/SSRS-E3008C?style=for-the-badge&logo=microsoft&logoColor=white)](https://docs.microsoft.com/en-us/sql/reporting-services)
[![AWS Redshift](https://img.shields.io/badge/AWS%20Redshift-8C4FFF?style=for-the-badge&logo=amazon-redshift&logoColor=white)](https://aws.amazon.com/redshift/)
[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)

*Designed and implemented by **Team 1** for ISTM 637 (Data Warehousing) at Texas A&M University*

</div>

---

## 📖 Project Overview

This project involves the comprehensive design and implementation of an enterprise-grade data warehouse for **Dominick's Finer Foods (DFF)**, a prominent Chicago-area supermarket chain. Utilizing the famous Kilts Center retail scanner dataset (~5 GB of store-level data spanning 1989–1994), we engineered a complete **Hybrid Data Pipeline** to transform raw OLTP files into actionable business intelligence.

Our solution supports end-to-end analytical processing, progressing from raw CSV source files to advanced BI dashboards, demonstrating proficiency in data modeling, ETL engineering, and multidimensional reporting.

---

## 🏗️ Architecture & Data Modeling

### Hybrid ETL Pipeline

The data moves through a rigorous ETL (Extract, Transform, Load) pipeline using **SQL Server Integration Services (SSIS)**. This hybrid architecture cleanses the operational data, derives missing metadata, manages surrogate keys, and populates the presentation layer.

<div align="center">
  <img src="assets/etl_pipeline_diagram.png" alt="ETL Pipeline Architecture" width="800"/>
</div>

### Dimensional Star Schema (Kimball Methodology)

To support our analytical queries, we designed an **Independent Data Mart** employing a pure star schema based on Ralph Kimball's bottom-up methodology. The warehouse centers around a highly granular `FactWeeklySales` table.

- **Grain:** One row per UPC × Store × Week
- **Volume:** ~15 Million Fact Rows
- **Dimensions:** Product, Store, Time, Category, Promotion

<div align="center">
  <img src="assets/star_schema_erd.png" alt="Star Schema ERD" width="800"/>
</div>

---

## 📊 Business Intelligence & Reporting

We developed BI solutions across four different enterprise platforms to answer critical business questions for DFF management.

### 1. Power BI (Store Demographics & Revenue Analyst)
*Business Question: Which stores fall into the top 25%, middle 50%, and bottom 25% of total Toothpaste revenue, and how do their demographics differ?*


### 2. AWS Redshift Query v.2 (Big Data Promotion Lift)
*Business Question: Which promotion type (Bonus Buy/Coupon/Sale) generated the highest incremental unit sales lift in the Canned Soup category?*


### 3. SQL Server Reporting Services (SSRS)
*Business Question: What were the total weekly unit sales of Soft Drinks across all stores for each week?*


### 4. SQL Server Analysis Services (SSAS Cubes)
*Business Question: How do promotion weeks compare to non-promotion weeks in terms of sales volume?*


---

## 📂 Repository Structure

The project was executed in four milestone phases, culminating in a fully integrated final report.

```text
dff-data-warehouse-project/
│
├── README.md                          ← Project showcase (You are here)
├── assets/                            ← Showcase images
│
├── report_1/                          ← Requirements, EDA, and BQ Formulation
├── report_2/                          ← Logical & Physical Design (Bus Matrix, Star Schema)
├── report_3/                          ← ETL Design & Implementation (SSIS, SQL Scripts)
└── report_4/                          ← Integrated Final Report & BI Deployments
    ├── Integrated_Report_4.docx       ← The final submitted comprehensive report
    ├── sql/                           ← All 8 robust SQL scripts for DB creation & ETL
    └── screenshots/                   ← 41 screenshots providing full implementation evidence
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|:---|:---|
| **Microsoft SQL Server 2016** | Core RDBMS, Data Staging, and Data Mart hosting |
| **SQL Server Integration Services (SSIS)** | ETL Engineering, Data Cleansing, and Pipeline Automation |
| **SQL Server Analysis Services (SSAS)** | Multidimensional Cube Design and OLAP processing |
| **SQL Server Reporting Services (SSRS)** | Parameterized and Paginated Operational Reporting |
| **Amazon Redshift (AWS)** | Cloud Data Warehousing and Analytical Query Execution |
| **Microsoft Power BI** | Interactive Dashboards, DAX calculations, and Geospatial Mapping |
| **LucidChart / Draw.io** | Architecture and Entity Relationship Diagramming |

---

<div align="center">
  <i>"Transforming retail transaction arrays into strategic business insights."</i>
</div>
