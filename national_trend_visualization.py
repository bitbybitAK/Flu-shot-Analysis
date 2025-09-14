import pandas as pd
import plotly.graph_objects as go
import numpy as np

INPUT_FILE = 'aggregated_data/year_agg.csv'
OUTPUT_FILE = 'national_trend.html'

def build_national_trend():
	# Load aggregated year data
	df = pd.read_csv(INPUT_FILE)
	# Ensure expected columns exist
	required = {'Season/Survey Year','avg_vaccination_rate','avg_ci_lower','avg_ci_upper'}
	missing = required - set(df.columns)
	if missing:
		raise ValueError(f"Missing required columns in {INPUT_FILE}: {missing}")

	# Sort by year
	df = df.sort_values('Season/Survey Year').reset_index(drop=True)

	# Compute CI band arrays
	x_years = df['Season/Survey Year']
	y_mean = df['avg_vaccination_rate']
	y_lower = df['avg_ci_lower']
	y_upper = df['avg_ci_upper']

	# Identify min/max years for annotations
	min_idx = y_mean.idxmin()
	max_idx = y_mean.idxmax()
	min_year, min_val = int(df.loc[min_idx, 'Season/Survey Year']), float(df.loc[min_idx, 'avg_vaccination_rate'])
	max_year, max_val = int(df.loc[max_idx, 'Season/Survey Year']), float(df.loc[max_idx, 'avg_vaccination_rate'])

	fig = go.Figure()

	# 95% CI shaded band
	fig.add_trace(go.Scatter(
		x=list(x_years) + list(x_years[::-1]),
		y=list(y_upper) + list(y_lower[::-1]),
		fill='toself',
		fillcolor='rgba(31, 119, 180, 0.15)',
		line=dict(color='rgba(31,119,180,0)'),
		name='95% CI',
		hoverinfo='skip'
	))

	# Mean line
	fig.add_trace(go.Scatter(
		x=x_years,
		y=y_mean,
		mode='lines+markers',
		name='U.S. Average Vaccination Rate',
		line=dict(color='rgb(31,119,180)', width=3),
		marker=dict(size=6),
		hovertemplate='Year: %{x}<br>Rate: %{y:.1f}%<extra></extra>'
	))

	# Policy-relevant markers
	policy_years = {
		2009: 'H1N1 (Swine Flu) pandemic',
		2018: 'Expanded county coverage',
		2020: 'COVID-19 pandemic begins',
		2021: 'COVID-19 vaccination campaigns'
	}
	for year, label in policy_years.items():
		if year in set(x_years):
			val = float(df.loc[df['Season/Survey Year']==year, 'avg_vaccination_rate'].iloc[0])
			fig.add_trace(go.Scatter(
				x=[year], y=[val],
				mode='markers',
				marker=dict(color='crimson', size=9, symbol='star'),
				name=f'{year}: {label}',
				hovertemplate=f'<b>{year}</b><br>{label}<br>Rate: %{{y:.1f}}%<extra></extra>'
			))

	# Annotate highest and lowest years
	fig.add_annotation(
		x=max_year, y=max_val,
		text=f'Highest: {max_year} ({max_val:.1f}%)',
		showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5,
		arrowcolor='green', bgcolor='rgba(255,255,255,0.9)',
		ax=40, ay=-40
	)
	fig.add_annotation(
		x=min_year, y=min_val,
		text=f'Lowest: {min_year} ({min_val:.1f}%)',
		showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5,
		arrowcolor='red', bgcolor='rgba(255,255,255,0.9)',
		ax=-40, ay=40
	)

	# Layout
	fig.update_layout(
		title={
			'text': 'U.S. Flu Vaccination Trend (2009–2023)<br><sub>Mean with 95% Confidence Interval</sub>',
			'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}
		},
		xaxis_title='Year',
		yaxis_title='Average Vaccination Rate (%)',
		width=1100, height=600,
		legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
		hovermode='x unified',
		margin=dict(l=60, r=30, t=80, b=80)
	)
	fig.update_xaxes(dtick=1)
	fig.update_yaxes(range=[0, 100])

	fig.write_html(OUTPUT_FILE)
	print(f'Saved: {OUTPUT_FILE}')

if __name__ == '__main__':
	build_national_trend()
