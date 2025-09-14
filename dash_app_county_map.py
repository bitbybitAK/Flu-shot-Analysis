import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

INPUT_FILE = 'Flu_shot_cleaned.csv'

STATE_FIPS_TO_NAME = {
	'01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
	'08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '11': 'District of Columbia',
	'12': 'Florida', '13': 'Georgia', '15': 'Hawaii', '16': 'Idaho', '17': 'Illinois', '18': 'Indiana',
	'19': 'Iowa', '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana', '23': 'Maine', '24': 'Maryland',
	'25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota', '28': 'Mississippi', '29': 'Missouri',
	'30': 'Montana', '31': 'Nebraska', '32': 'Nevada', '33': 'New Hampshire', '34': 'New Jersey',
	'35': 'New Mexico', '36': 'New York', '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio',
	'40': 'Oklahoma', '41': 'Oregon', '42': 'Pennsylvania', '44': 'Rhode Island', '45': 'South Carolina',
	'46': 'South Dakota', '47': 'Tennessee', '48': 'Texas', '49': 'Utah', '50': 'Vermont', '51': 'Virginia',
	'53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming',
	'60': 'American Samoa', '66': 'Guam', '69': 'Northern Mariana Islands', '72': 'Puerto Rico', '78': 'U.S. Virgin Islands'
}

STATE_OPTIONS = [{'label': 'All States', 'value': 'ALL'}] + [
	{'label': name, 'value': code} for code, name in sorted(STATE_FIPS_TO_NAME.items(), key=lambda x: x[1])
]


def aggregate_county_year(df: pd.DataFrame) -> pd.DataFrame:
	grp = df.groupby(['Geography', 'FIPS', 'Season/Survey Year'], as_index=False).agg(
		avg_rate=('Estimate (%)', 'mean'),
		avg_ci_lower=('ci_lower', 'mean'),
		avg_ci_upper=('ci_upper', 'mean'),
		record_count=('Estimate (%)', 'count'),
		sample_size_nonnull=('Sample Size', lambda s: s.dropna().sum())
	)
	grp['sample_size'] = grp['sample_size_nonnull'].replace(0, np.nan)
	grp['sample_size'] = grp['sample_size'].fillna(grp['record_count'])
	grp.drop(columns=['sample_size_nonnull'], inplace=True)
	grp['FIPS'] = grp['FIPS'].astype(str).str.zfill(5)
	grp['STATEFP'] = grp['FIPS'].str[:2]
	return grp


def make_map(ds: pd.DataFrame, title: str) -> go.Figure:
	fig = go.Figure(go.Choropleth(
		locations=ds['FIPS'], z=ds['avg_rate'], text=ds['Geography'], locationmode='geojson-id',
		colorscale='RdYlGn', reversescale=False, marker_line_color='white', marker_line_width=0.3,
		zmin=0, zmax=100, colorbar_title='Rate (%)',
		customdata=np.column_stack((ds['Season/Survey Year'], ds['avg_ci_lower'], ds['avg_ci_upper'], ds['sample_size'], ds['record_count'])),
		hovertemplate='<b>%{text}</b><br>' +
			'FIPS: %{location}<br>Year: %{customdata[0]}<br>' +
			'Rate: %{z:.1f}%<br>95% CI: %{customdata[1]:.1f}–%{customdata[2]:.1f}%<br>' +
			'Sample Size: %{customdata[3]:.0f} (records: %{customdata[4]})<extra></extra>'
	))
	fig.update_layout(
		title={'text': title, 'x': 0.5},
		geo=dict(
			scope='usa', projection=go.layout.geo.Projection(type='albers usa'),
			showlakes=True, lakecolor='rgb(255,255,255)',
			showland=True, landcolor='rgb(217,217,217)'
		),
		margin=dict(l=0, r=0, t=50, b=0), height=650
	)
	return fig


# Load and prepare data once
_df_raw = pd.read_csv(INPUT_FILE)
_df = aggregate_county_year(_df_raw)
YEARS = sorted(_df['Season/Survey Year'].unique())

app = Dash(__name__)
app.title = 'US County Flu Vaccination Map'

app.layout = html.Div([
	html.H2('U.S. County Flu Vaccination Rates – Interactive Explorer'),
	html.Div([
		html.Div([
			html.Label('State Filter'),
			dcc.Dropdown(options=STATE_OPTIONS, value='ALL', id='state-filter', clearable=False),
		], style={'flex': '1', 'minWidth': '250px', 'marginRight': '16px'}),
		html.Div([
			html.Label('Left Year'),
			dcc.Dropdown(options=[{'label': str(y), 'value': y} for y in YEARS], value=YEARS[0], id='year-left', clearable=False),
		], style={'flex': '1', 'minWidth': '150px', 'marginRight': '16px'}),
		html.Div([
			html.Label('Right Year'),
			dcc.Dropdown(options=[{'label': str(y), 'value': y} for y in YEARS], value=YEARS[-1], id='year-right', clearable=False),
		], style={'flex': '1', 'minWidth': '150px'}),
	], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '12px'}),

	html.Div([
		html.Div([dcc.Graph(id='map-left')], style={'flex': '1', 'minWidth': '500px', 'marginRight': '8px'}),
		html.Div([dcc.Graph(id='map-right')], style={'flex': '1', 'minWidth': '500px', 'marginLeft': '8px'}),
	], style={'display': 'flex', 'flexWrap': 'wrap'})
])


@app.callback(
	Output('map-left', 'figure'),
	Output('map-right', 'figure'),
	Input('state-filter', 'value'),
	Input('year-left', 'value'),
	Input('year-right', 'value')
)
def update_maps(state_code, year_left, year_right):
	if state_code == 'ALL':
		df_left = _df[_df['Season/Survey Year'] == year_left]
		df_right = _df[_df['Season/Survey Year'] == year_right]
		title_left = f'All States – {year_left}'
		title_right = f'All States – {year_right}'
	else:
		df_left = _df[(_df['Season/Survey Year'] == year_left) & (_df['STATEFP'] == state_code)]
		df_right = _df[(_df['Season/Survey Year'] == year_right) & (_df['STATEFP'] == state_code)]
		state_name = STATE_FIPS_TO_NAME.get(state_code, state_code)
		title_left = f'{state_name} – {year_left}'
		title_right = f'{state_name} – {year_right}'

	fig_left = make_map(df_left, title_left)
	fig_right = make_map(df_right, title_right)
	return fig_left, fig_right


if __name__ == '__main__':
	app.run_server(host='0.0.0.0', port=8050, debug=False)
