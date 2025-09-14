# Flu Vaccination Analysis Dashboard

A comprehensive analysis of flu vaccination trends across U.S. counties from 2009-2023, revealing significant disparities and opportunities for public health intervention.

## Overview

This project analyzes over 200,000 flu vaccination records across 1,944 counties to understand vaccination patterns, identify disparities, and provide actionable insights for healthcare providers and policymakers.

## Key Findings

### National Trends Show Concerning Decline
The data reveals a troubling pattern: while flu vaccination rates peaked around 2019-2021 (39%+ average), there's been a notable decline to 33.9% in 2023. This downward trend coincides with the COVID-19 pandemic, suggesting potential resource diversion or public health fatigue.

### Geographic Disparities Are Stark
County-level analysis uncovers dramatic differences in vaccination uptake:
- **Top performers**: Lower Connecticut River Valley (58.5%), Newport, RI (56.1%), Arlington, VA (55.0%)
- **Bottom performers**: Region 4, FL (18.0%), Starr, TX (20.1%), Nevada, CA (22.3%)

The 40+ percentage point gap between highest and lowest performing counties highlights significant inequities in healthcare access and public health infrastructure.

### Setting Matters More Than Expected
Where people get vaccinated reveals critical insights:
- **Medical settings**: Consistently highest rates (51-87% across age groups)
- **Workplace settings**: Alarmingly low (1-18% across all demographics)
- **Pharmacy/Store**: Moderate performance (7-40%)

This suggests that traditional workplace wellness programs are failing to reach employees effectively, while medical settings remain the most trusted vaccination venues.

### Age Disparities Persist
Children (6 months - 17 years) show the lowest overall rates at 29.1%, but interestingly, when they do get vaccinated, it's overwhelmingly in medical settings (86.7%). This indicates that pediatric vaccination relies heavily on healthcare provider recommendations rather than community-based programs.

### Racial and Ethnic Gaps Are Narrower Than Expected
While disparities exist, the range is relatively narrow:
- Asian, Non-Hispanic: 40.6%
- Black, Non-Hispanic: 33.3%

The 7.3 percentage point difference, while statistically significant, suggests that systemic barriers affect all groups, though some more than others.

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Dashboard
```bash
python multi_tab_dashboard.py
```
Then open http://localhost:8050 in your browser.

### Exploring Visualizations
Check the `visualizations/` folder for individual HTML charts that can be opened directly in your browser.

## Project Structure

```
├── multi_tab_dashboard.py              # Interactive Dash dashboard
├── Flu_shot_cleaned.csv               # Processed dataset (202K records)
├── aggregated_data/                    # Analysis-ready datasets
├── visualizations/                     # Interactive HTML charts
├── documentation/                      # Analysis documentation
└── requirements.txt                    # Python dependencies
```

## Data Sources

- **Primary Dataset**: 202,508 county-level flu vaccination records
- **Time Period**: 2009-2023 (15 years)
- **Geographic Coverage**: 1,944 counties across all 50 states
- **Demographic Dimensions**: Age groups, race/ethnicity, vaccination settings
- **Statistical Rigor**: 95% confidence intervals for all estimates

## Key Insights for Public Health

### Immediate Actions Needed
1. **Target Low-Performing Counties**: Focus resources on bottom 20% (rates <30%)
2. **Address Workplace Gaps**: Implement effective workplace vaccination programs
3. **Pediatric Outreach**: Develop community-based programs for children
4. **Rural Access**: Deploy mobile vaccination services to underserved areas

### Policy Recommendations
1. **Geographic Equity**: Ensure all counties achieve minimum 30% coverage
2. **Setting Diversification**: Expand beyond medical settings to pharmacies and workplaces
3. **Demographic Targeting**: Develop culturally appropriate outreach programs
4. **Data Infrastructure**: Implement real-time monitoring systems

## Technical Features

- **Interactive Dashboards**: Multi-tab interface with filtering and hover details
- **Geographic Mapping**: FIPS-based choropleth maps with state/county selection
- **Statistical Rigor**: Error bars, confidence intervals, outlier highlighting
- **Responsive Design**: Works across devices and screen sizes

## Contributing

This analysis provides a foundation for ongoing flu vaccination monitoring and improvement. The codebase is designed for extensibility and can be adapted for other vaccination types or geographic regions.

---

*This analysis represents a comprehensive approach to public health data science, transforming raw vaccination data into actionable insights that can improve health outcomes for millions of Americans.*
