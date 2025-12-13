# YouTube Video Length & Engagement Analysis

This repository analyzes how **video length influences engagement on YouTube**, using real-world data and statistical testing. The project compares **short-form videos (<10 minutes)** and **long-form videos (>20 minutes)** across multiple content categories to determine whether duration predicts stronger audience interaction.

---

## 📌 Project Overview

Engagement plays a major role in YouTube visibility and recommendations. This project investigates whether shorter videos generate higher proportional engagement by analyzing the **like-to-view ratio** across videos from different categories.

**Key Question:**  
Do short YouTube videos receive higher engagement than long videos?

---

## 📊 Dataset

- **Total videos:** 221  
- **Categories:**  
  - Gaming  
  - Music  
  - How-to & Style  
  - Science & Technology  
- **Video groups:**  
  - Short: under 10 minutes  
  - Long: over 20 minutes  

Each record includes:
- Video ID & title  
- Duration  
- Category  
- View count  
- Like count  
- Comment count  
- Like-to-view ratio (engagement metric)

Dataset file:  
- `youtube_length_engagement.csv`

---

## 🔬 Methodology

1. **Data Collection**
   - Collected using the **YouTube Data API v3**
   - Automated searches by category and duration
   - Invalid or incomplete entries removed

2. **Engagement Metric**
   - Engagement defined as:  
     ```
     likes / views
     ```
   - Allows fair comparison across videos of different sizes

3. **Statistical Analysis**
   - Normality tested using **Shapiro–Wilk**
   - Group comparison using **Mann–Whitney U test**
   - Effect size measured with **Cohen’s d**

---

## 📈 Key Findings

- **Short videos show significantly higher engagement** than long videos  
- Short videos achieved ~**73% higher like-to-view ratios**
- Results are **statistically significant** (p < 0.001) with a **large effect size**
- Category-level differences exist:
  - Strong short-video advantage in *Science & Technology* and *Gaming*
  - *Music* is an exception where long videos perform better

Visualization:  
- `youtube_engagement_analysis.png`

---

## 🧠 Insights

- Shorter videos require less viewer commitment, increasing the likelihood of interaction
- Concise, focused content tends to perform better in information-driven categories
- Engagement patterns align with YouTube’s recommendation dynamics favoring early interactions

---

## 🗂️ Repository Structure

```text
├── engagement_analysis.py          # Data analysis, statistics, and visualization
├── youtube_data.py                 # YouTube API data collection and preprocessing
├── youtube_length_engagement.csv   # Final cleaned dataset
├── youtube_engagement_analysis.png # Engagement visualizations
└── README.md
