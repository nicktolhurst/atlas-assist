from flexmock import flexmock
from atlas.extensions.radarr.ext.radarr_api import RadarrAPI
import json

mock_radarr_api = flexmock(RadarrAPI)

# Mock the __init__ method
mock_radarr_api.should_receive('__init__').and_return(None)

# Mock the search_top_match method
with open('atlas/extensions/radarr/tests/mock_data/radarr_api_search_top_match.json', 'r') as f:
    mock_search_top_match_response = json.load(f)
    
mock_radarr_api.should_receive('search_top_match').with_args('search_term').and_return(mock_search_top_match_response, None)

# Mock the download_movie method
mock_radarr_api.should_receive('download_movie').with_args({'tmdbId': 123}, 4, '/data/media/movies/').and_return("Movie downloaded.")