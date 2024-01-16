import os
from .utils import extract_search_term
from atlas.extension_router import AtlasExtension
from .radarr_api import RadarrAPI


RADARR_API_KEY = os.environ.get('RADARR_EXT_RADARR_API_KEY')
RADARR_API_BASE_URL = 'https://atla.s/rdr'
SEARCH_TERM_CONTEXT_SYSTEM_MSG = "Ask the user to specify the name of the media to search for."
CATEGORY_CONTEXT_SYSTEM_MSG = "Ask the user to specify a category (movie or tv series). They should not be a 'yes' or 'no' question."


class RadarrExtension(AtlasExtension):
    def __init__(self, logger, radar_api = None):
        super().__init__()
        self.log = logger
        self.radarr_api = radar_api if radar_api is not None else RadarrAPI(RADARR_API_BASE_URL, RADARR_API_KEY, logger)
        
        
    def can_handle_input(self, voice_input):
        return 'download' in voice_input
    
    
    def process_voice_input(self, voice_input):        
        
        search_term = extract_search_term(
            input = voice_input, 
            regex = r'(movie|tv series|tv show|series|download me the movie|download the movie|watch the movie|download|watch)(.*?)(\.|,|for|it|$)'
            )
        
        if not search_term:
            return self.request_further_context(SEARCH_TERM_CONTEXT_SYSTEM_MSG)
        
        return self._search_and_download_movie(search_term)
                
                
    def process_follow_up_input(self, follow_up_input):
        if 'search_term' not in self.conversation_context:
            self.log.debug('Adding search term to context')
            self.conversation_context['search_term'] = follow_up_input
            
        self.log.debug(f"Follow-up input: {follow_up_input} with context {self.conversation_context}")
        self.end_conversation()
        return self._search_and_download_movie(self.conversation_context['search_term'])
    
    
    def _search_and_download_movie(self, search_term):
        movie, system_msg = self.radarr_api.search_top_match(search_term)
        
        if not movie and system_msg:
            return system_msg

        return self.radarr_api.download_movie(movie)

