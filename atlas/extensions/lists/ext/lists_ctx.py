import re


class Context:
    def __init__(self, logger):
        self.log = logger
        self.voice_input = None
        self.action = None
        self.item = None
        self.list = None

    def extract_from_input(self, voice_input):
        self.voice_input = voice_input
        
        intent_to_read_regex = re.compile(r"(read(?: out)?|what is (?:on|in)|tell me what is (?:on|in)) (?:me )?the (.*?) list", re.IGNORECASE)
        intent_to_read = intent_to_read_regex.search(self.voice_input)
        if intent_to_read:
            self.action = 'read'
            self.list = intent_to_read.group(2)
            return
        
        extraction_methods = {
            'add': self._extract_add_context,
            'remove': self._extract_remove_context,
            'create': self._extract_create_context,
            'delete': self._extract_delete_context,
        }
            
        words = voice_input.split()
        
        for action_key in extraction_methods:
            if action_key in words:
                self.action = action_key
                self.log.debug(f"Extracting context for action: {action_key}")
                extraction_methods[action_key]()
        

    def _extract_add_context(self):
        regex = re.compile(r"add (.*?) to (?:the |my )?(.*?) list", re.IGNORECASE)
        match = regex.search(self.voice_input)
        self.item, self.list = (match.groups() if match else (None, None))

    def _extract_remove_context(self):
        regex =  re.compile(r"remove (.*?) from (?:the |my )?(.*?) list", re.IGNORECASE)
        match = regex.search(self.voice_input)
        self.item, self.list = (match.groups() if match else (None, None))

    def _extract_create_context(self):
        first_pattern = re.compile(r"create(?: me)? a(?: new)? (?:list called )?['\"]?([^'\"]+?)['\"]?(?: list)?(?=\?| for me|$)", re.IGNORECASE)
        second_pattern = re.compile(r"create the list ['\"]?([^'\"]+)['\"]?", re.IGNORECASE)
        match = first_pattern.search(self.voice_input)
        self.log.debug(f"Match 1: {match}")
        if not match:
            match = second_pattern.search(self.voice_input)
            self.log.debug(f"Match 2: {match}")
        if not match:
            self.log.error(f"Unable to match '{self.voice_input}' against regex.")
        self.list = match.group(1) if match else None

    def _extract_delete_context(self):
        regex = re.compile(r"delete(?: the)?(?: list called)? ['\"]?([^'\"]+?)['\"]?(?: list)?(?=\?|$)", re.IGNORECASE)
        match = regex.search(self.voice_input)
        
        self.list = match.group(1) if match else None