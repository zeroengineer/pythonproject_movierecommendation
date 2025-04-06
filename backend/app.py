from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load and clean dataset
df = pd.read_csv('imdb_top_1000.csv')

# Clean and prepare data
df['IMDB_Rating'] = pd.to_numeric(df['IMDB_Rating'], errors='coerce')
df['Meta_score'] = pd.to_numeric(df['Meta_score'], errors='coerce')
df['No_of_Votes'] = pd.to_numeric(df['No_of_Votes'], errors='coerce')
df['Gross'] = pd.to_numeric(df['Gross'].replace('[^\d.]', '', regex=True), errors='coerce')
df.fillna('', inplace=True)

# Define searchable columns
searchable_columns = [
    'Series_Title', 'Released_Year', 'Certificate', 'Runtime', 'Genre',
    'IMDB_Rating', 'Overview', 'Meta_score', 'Director',
    'Star1', 'Star2', 'Star3', 'Star4', 'No_of_Votes', 'Gross'
]

@app.route('/search')
def search():
    filters = request.args
    results = df.copy()

    for key in filters:
        if key in searchable_columns and filters[key]:
            # Support multiple comma-separated filter values
            queries = [q.strip().lower() for q in filters[key].split(',') if q.strip()]
            results = results[results[key].astype(str).str.lower().apply(
                lambda val: any(q in val for q in queries)
            )]

    return jsonify(results[searchable_columns + ['Poster_Link']].to_dict(orient='records'))

@app.route('/suggestions')
def suggestions():
    field = request.args.get('field')
    if field in searchable_columns:
        unique_values = df[field].astype(str).unique()
        return jsonify(sorted([val for val in unique_values if val and val != 'nan']))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
