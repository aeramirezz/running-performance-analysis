# Running Performance Analysis 🏃

## Motivation

I started running back in high school, but it wasn't until 2020 that it truly became part of my life. In Peru, the mandatory lockdown was long and intense. Running was one of the few reasons you could go outside, and for me, it became a way to disconnect from the stress and anxiety that came with that period. Putting on my headphones and hitting the streets gave me a sense of freedom I couldn't find anywhere else.

What started as a way to cope slowly turned into something more. A habit, a discipline, and eventually a passion. I ran my first half marathon and started training for a full one, until an injury forced me to stop and reset. Today I run for the joy of it, not for competition. It keeps me grounded, and someday I'd like to complete that marathon just to prove I can.

Over the years, without really thinking about it, my Apple Watch recorded every single one of those runs. Pace, heart rate, distance, elevation, weather conditions. Nearly 7 years of data, sitting there. This project is my attempt to make sense of it.

---

## Project Overview

A full data analysis pipeline applied to personal running data exported from Apple Health (2019–2026). The goal is to explore performance trends, identify training patterns, and build predictive models using the same tools and workflow a data analyst would use in a professional setting.

**Stack:** Python · SQL · Power BI

---

## Dataset

Personal running data exported from Apple Health, recorded via Apple Watch between May 2019 and March 2026. After cleaning, the dataset contains 429 running sessions and 19 features including pace, distance, heart rate, elevation, weather conditions, and pause data.

Raw data is not included in this repository for privacy reasons.

---

## Project Structure

```
running-performance-analysis/
│
├── data/
│   ├── raw/              # Original export from Apple Health (not tracked)
│   └── processed/        # Cleaned and enriched dataset
│
├── scripts/
│   ├── 01_cleaning.py    # Data cleaning and feature engineering
│   ├── 02_eda.py         # Exploratory data analysis
│   ├── 03_clustering.py  # Unsupervised clustering of training sessions
│   └── 04_model.py       # Predictive model (pace forecasting)
│
├── dashboard/            # Power BI dashboard files
├── .gitignore
└── README.md
```

---

## Analysis Roadmap

- [x] Data extraction from Apple Health XML
- [x] Data cleaning and feature engineering
- [ ] Exploratory data analysis (EDA)
- [ ] Clustering of training session types
- [ ] Pace prediction model
- [ ] Power BI dashboard

---

## Key Questions

- How has my pace and endurance evolved over 7 years?
- Do I perform better in certain conditions (weather, time of day, day of week)?
- Can unsupervised learning identify distinct training patterns in my runs?
- Can I predict my pace based on recent training data?
