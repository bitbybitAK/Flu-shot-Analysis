import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

INPUT_FILE = 'aggregated_data/county_year_agg.csv'
OUTPUT_FILE = 'county_small_multiples.html'

# Configuration
NUM_COUNTIES = 24  # number of counties to plot (adjust as needed)
GRID_ROWS = 4
GRID_COLS = 6


def select_counties(df: pd.DataFrame, n: int) -> pd.Index:
	"""Select a representative set of counties with sufficient data across years.
	Strategy: prefer counties with more years; then highest variance (interesting trends).
	"""
	years_per_county = df.groupby('Geography')['Season/Survey Year'].nunique()
	var_per_county = df.groupby('Geography')['avg_vaccination_rate'].var().fillna(0)
	summary = (
		pd.concat([
			years_per_county.rename('num_years'),
			var_per_county.rename('rate_variance')
		], axis=1)
		.reset_index()
	)
	# Score: prioritize many years, then higher variance
	summary['score'] = summary['num_years'].rank(pct=True) * 0.7 + summary['rate_variance'].rank(pct=True) * 0.3
	selected = summary.sort_values(['score','num_years','rate_variance'], ascending=False)['Geography'].head(n)
	return selected


def build_small_multiples():
	# Load data
	df = pd.read_csv(INPUT_FILE)

	# Compute national average per year
	national = df.groupby('Season/Survey Year', as_index=False)['avg_vaccination_rate'].mean()
	national.rename(columns={'avg_vaccination_rate': 'national_avg'}, inplace=True)

	# Select counties to display
	selected_counties = select_counties(df, NUM_COUNTIES)
	df_sel = df[df['Geography'].isin(selected_counties)].copy()

	# Merge national average for reference
	df_sel = df_sel.merge(national, on='Season/Survey Year', how='left')

	# Determine line color per county based on mean diff vs national
	def county_color(sub: pd.DataFrame) -> str:
		# Compare only overlapping years
		if sub.empty:
			return 'gray'
		diff = (sub['avg_vaccination_rate'] - sub['national_avg']).mean()
		return 'green' if diff >= 0 else 'crimson'

	county_to_color = {c: county_color(df_sel[df_sel['Geography'] == c]) for c in selected_counties}

	# Build subplot grid
	fig = make_subplots(rows=GRID_ROWS, cols=GRID_COLS,
		subplot_titles=[str(c) for c in selected_counties],
		shared_xaxes=True, shared_yaxes=True)

	# Add traces per county
	row, col = 1, 1
	for county in selected_counties:
		sub = df_sel[df_sel['Geography'] == county].sort_values('Season/Survey Year')
		color = county_to_color[county]

		# County line
		fig.add_trace(
			go.Scatter(
				x=sub['Season/Survey Year'], y=sub['avg_vaccination_rate'],
				mode='lines+markers', name=str(county),
				line=dict(color=color, width=2), marker=dict(size=4),
				hovertemplate=f'<b>{county}</b><br>Year: %{{x}}<br>Rate: %{{y:.1f}}%<extra></extra>'
			),
			row=row, col=col
		)

		# National average line (as thin gray line)
		nat = national.copy()
		fig.add_trace(
			go.Scatter(
				x=nat['Season/Survey Year'], y=nat['national_avg'],
				mode='lines', name='National Avg',
				line=dict(color='gray', width=1, dash='dash'),
				hovertemplate='Year: %{x}<br>National: %{y:.1f}%<extra></extra>',
				showlegend=False
			),
			row=row, col=col
		)

		# Advance grid position
		col += 1
		if col > GRID_COLS:
			col = 1
			row += 1
			if row > GRID_ROWS:
				break

	# Global layout
	fig.update_layout(
		title={
			'text': 'County Flu Vaccination Trends (Small Multiples)<br><sub>Line color indicates overall performance vs national average (green = above, red = below)</sub>',
			'x': 0.5, 'xanchor': 'center'
		},
		width=1500, height=900,
		margin=dict(l=60, r=20, t=100, b=60),
		hovermode='closest'
	)
	fig.update_xaxes(dtick=2)
	fig.update_yaxes(range=[0, 100])

	fig.write_html(OUTPUT_FILE)
	print(f'Saved: {OUTPUT_FILE}')

if __name__ == '__main__':
	build_small_multiples()
