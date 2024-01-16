import os
from .utils import extract_search_term
from atlas.extension_router import AtlasExtension
from .radarr_api import RadarrAPI


RADARR_API_KEY = os.environ.get('RADARR_EXT__API_KEY')
RADARR_API_BASE_URL =  os.environ.get('RADARR_EXT__API_KEY')

SEARCH_TERM_CONTEXT__SYSTEM_MSG = "Ask the user to specify the name of the media to search for."
CATEGORY_CONTEXT__SYSTEM_MSG = "Ask the user to specify a category (movie or tv series). They should not be a 'yes' or 'no' question."
MOVIE_ALREADY_IN_LIBRARY__SYSTEM_MSG = "Let the user know that the movie is already in the library."
MOVIE_ALREADY_BEING_MONITORED__SYSTEM_MSG = "Let the user know that the movie is already being monitored."
MOVIE_IS_NOT_AVAILABLE_FOR_DOWNLOAD__SYSTEM_MSG = "Let the user know that the movie is not available for download yet."

class RadarrExtension(AtlasExtension):
    def __init__(self, logger, radar_api = None):
        super().__init__()
        self.log = logger
        self.radarr_api = radar_api if radar_api is not None else RadarrAPI(RADARR_API_BASE_URL, RADARR_API_KEY, logger)
        
    """
    Used by the extension router to determine whether this extension can handle the given voice input. 
    """  
    def can_handle_input(self, voice_input):
        return 'download' in voice_input
    
    
    """
    Processes the voice input by extracting the search term. If the search term is not found, the extension will request 
    further context from the user. Ifd the search term is found, the extension will download the movie.
    
    """
    def process_voice_input(self, voice_input):        
        
        search_term = extract_search_term(
            input = voice_input, 
            regex = r'(movie|tv series|tv show|series|download me the movie|download the movie|watch the movie|download|watch)(.*?)(\.|,|for|it|$)'
            )
        
        if not search_term:
            # Requesting further context also starts a conversation. This is used to route the follow-up input to this extension.
            return self.request_further_context(SEARCH_TERM_CONTEXT__SYSTEM_MSG, start_conversation=True)
        
        return self._add_to_downloads(search_term)
                
    """
    Called by the extension router when the user has provided further context. The extension will process the follow-up context by
    taking the adding taking the search term from the follow_up_input and downloading the movie.
    """       
    def process_follow_up_input(self, follow_up_input):
        if 'search_term' not in self.conversation_context:
            self.conversation_context['search_term'] = follow_up_input
            
        # End the conversation before downloading the movie, otherwise you will be trapped!
        self.end_conversation()
        return self._add_to_downloads(self.conversation_context['search_term'])
    
    
    def _add_to_downloads(self, search_term):
        # Search for the top matching movie 
        movie, system_msg = self.radarr_api.search_top_match(search_term)
        if system_msg:
            return system_msg
        
        # Perform a series of checks to determine if the movie can be downloaded
        system_msg = self._check_movie_state(movie)
        if system_msg:
            return system_msg

        # Download the movie
        return self.radarr_api.download_movie(movie)

    def _check_movie_state(self, movie):
        if movie.get('hasFile'):
            return MOVIE_ALREADY_IN_LIBRARY__SYSTEM_MSG
        
        if movie.get('monitored'):
            return MOVIE_ALREADY_BEING_MONITORED__SYSTEM_MSG
        
        if movie.get('isAvailable') is False or movie.get('status') != 'released':
            return MOVIE_IS_NOT_AVAILABLE_FOR_DOWNLOAD__SYSTEM_MSG
        
        return None