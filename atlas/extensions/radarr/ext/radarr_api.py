import json
import requests
from urllib.parse import quote

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RadarrAPI:
    def __init__(self, base_url, api_key, logger):
        self.base_url = base_url
        self.api_key = api_key
        self.log = logger

    def search_top_match(self,search_term):
        try:
            url = f"{self.base_url}/api/v3/movie/lookup?term={quote(search_term)}"
            self.log.debug(f"Searching for movie: '{search_term}' with url: '{url}'")
            headers = {
                'X-Api-Key': self.api_key
            }
            response = requests.get(url, headers=headers, verify=False)

            if response.status_code == 200:
                if response.text is None:
                    return None, "Tell the user something went wrong with the response text."
                
                movie = response.json()[0]
                
                self.log.debug(json.dumps(movie, indent=4))
                
                return {
                    'tmdbId': movie.get('tmdbId'),
                    'title': movie.get('title'),
                    'year': movie.get('year'),
                    'overview': movie.get('overview'),
                    'status': movie.get('status'),
                    'ratings': movie.get('ratings'),
                    'hasFile': movie.get('hasFile'),
                    'monitored': movie.get('monitored'),
                    'isAvailable': movie.get('isAvailable'),
                }, None
            else:
                return None, f"Tell the user there was a HTTP error with status code {response.status_code} when trying to search for the movie."
        except Exception as e:
            return None, f"Tell the user something went wrong when trying to search for the movie. The exception was: {e}"

    def download_movie(self, movie, quality_profile_id=4, root_folder_path='/data/media/movies/'):
        if movie.get('hasFile'):
            return "Let the user know that the movie is already in the library."
        
        if movie.get('monitored'):
            return "Let the user know that the movie is already being monitored."
        
        if movie.get('isAvailable') is False or movie.get('status') != 'released':
            return "Let the user know that the movie is not available."
        
        # Data for the movie to add
        movie_data = {
            'tmdbId': movie.get('tmdbId'),
            'title': movie.get('title'), 
            'qualityProfileId': quality_profile_id,
            'year': movie.get('year'),
            'rootFolderPath': root_folder_path,
            'monitored': True,
            'addOptions': {
                'searchForMovie': True
            }
        }
        
        self.log.debug(f"Adding movie: '{json.dumps(movie_data, indent=4)}'")
        
        url = f"{self.base_url}/api/v3/movie"
        headers = {
            'X-Api-Key': self.api_key
        }
    
        try:
            response = requests.post(url, headers=headers, json=movie_data, verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.log.error(f"Error adding movie: {response.text}")
            return f"Let the user know that something went wrong. The exception was: {e}"
        if response.status_code == 201:
            return "Don't worry. This is only a proof of concept. Just let the user know that the movie was added to the download queue and should be ready shortly."
        else:
            self.log.error(f"Status code was not 201: {response.status_code}")
            self.log.error(f"Error adding movie: {response.text}")