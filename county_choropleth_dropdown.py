import pandas as pd
import numpy as np
import plotly.graph_objects as go

INPUT_FILE = 'Flu_shot_cleaned.csv'
OUTPUT_FILE = 'county_choropleth_dropdown.html'


def aggregate_county_year(df: pd.DataFrame) -> pd.DataFrame:
	# Compute per county-year aggregates
	grp = df.groupby(['Geography', 'FIPS', 'Season/Survey Year'], as_index=False).agg(
		avg_rate=('Estimate (%)', 'mean'),
		avg_ci_lower=('ci_lower', 'mean'),
		avg_ci_upper=('ci_upper', 'mean'),
		record_count=('Estimate (%)', 'count'),
		sample_size_nonnull=('Sample Size', lambda s: s.dropna().sum())
	)
	# If sample size is missing or zero, fall back to record_count
	grp['sample_size'] = grp['sample_size_nonnull'].replace(0, np.nan)
	grp['sample_size'] = grp['sample_size'].fillna(grp['record_count'])
	grp.drop(columns=['sample_size_nonnull'], inplace=True)
	return grp


def build_map_with_dropdown(df: pd.DataFrame):
	years = sorted(df['Season/Survey Year'].unique())

	fig = go.Figure()

	# Build a choropleth trace per year
	for i, year in enumerate(years):
		ds = df[df['Season/Survey Year'] == year].copy()
		# Ensure FIPS are strings, zero-padded to 5
		ds['FIPS'] = ds['FIPS'].astype(str).str.zfill(5)

		fig.add_trace(go.Choropleth(
			locations=ds['FIPS'],
			z=ds['avg_rate'],
			text=ds['Geography'],
			locationmode='geojson-id',
			colorscale='RdYlGn',
			reversescale=False,
			marker_line_color='white',
			marker_line_width=0.3,
			zmin=0, zmax=100,
			colorbar_title='Vaccination Rate (%)',
			visible=(i == 0),
			customdata=np.column_stack((
				ds['Season/Survey Year'],
				ds['avg_ci_lower'], ds['avg_ci_upper'],
				ds['sample_size'], ds['record_count']
			)),
			hovertemplate='<b>%{text}</b><br>' +
				'FIPS: %{location}<br>' +
				'Year: %{customdata[0]}<br>' +
				'Vaccination Rate: %{z:.1f}%<br>' +
				'95% CI: %{customdata[1]:.1f}% - %{customdata[2]:.1f}%<br>' +
				'Sample Size: %{customdata[3]:.0f} (records: %{customdata[4]})<extra></extra>'
		))

	# Dropdown buttons to toggle year visibility
	buttons = []
	for i, year in enumerate(years):
		visible = [False] * len(years)
		visible[i] = True
		buttons.append(dict(
			label=str(year),
			method='update',
			args=[{'visible': visible}, {'title': f'U.S. County Flu Vaccination Rates - {year}'}]
		))

	fig.update_layout(
		title={
			'text': f'U.S. County Flu Vaccination Rates - {years[0]}<br><sub>Use the dropdown to switch years</sub>',
			'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}
		},
		geo=dict(
			scope='usa',
			projection=go.layout.geo.Projection(type='albers usa'),
			showlakes=True, lakecolor='rgb(255,255,255)',
			showland=True, landcolor='rgb(217,217,217)',
			showocean=True, oceancolor='rgb(230,245,255)',
			showrivers=True, rivercolor='rgb(255,255,255)',
			showcoastlines=True, coastlinecolor='rgb(255,255,255)'
		),
		updatemenus=[dict(
			active=0,
			buttons=buttons,
			direction='down',
			x=0.02, xanchor='left',
			y=1.12, yanchor='top'
		)],
		width=1200, height=750,
		margin=dict(l=0, r=0, t=80, b=0)
	)

	fig.write_html(OUTPUT_FILE)
	print(f'Saved: {OUTPUT_FILE}')


def main():
	print('Loading cleaned dataset...')
	df = pd.read_csv(INPUT_FILE)
	print('Aggregating county-year metrics...')
	agg = aggregate_county_year(df)
	print(f'Years: {sorted(agg["Season/Survey Year"].unique())}')
	build_map_with_dropdown(agg)

if __name__ == '__main__':
	main()
