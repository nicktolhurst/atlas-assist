from abc import ABC, abstractmethod


class AtlasExtension(ABC):
    def __init__(self):
        # Flag to indicate if the extension is in a conversation
        self.in_conversation = False
        # Dictionary to store context relevant to the current conversation
        self.conversation_context = {}

    def start_conversation(self, context=None):
        """
        Start a conversation with the user.
        :param context: Optional context of the conversation.
        """
        self.in_conversation = True
        self.conversation_context = context if context else {}

    def end_conversation(self):
        """
        End the current conversation, resetting the conversation state.
        """
        self.in_conversation = False

    def is_in_conversation(self):
        """
        Check if the extension is currently in a conversation.
        :return: Boolean indicating if in conversation.
        """
        return self.in_conversation

    @abstractmethod
    def can_handle_input(self, voice_input):
        """
        Determines if the extension can handle the given input.
        This method must be implemented by the subclass.
        :param voice_input: The voice input to check.
        :return: Boolean indicating if the extension can handle the input.
        """
        pass

    @abstractmethod
    def process_voice_input(self, voice_input):
        """
        Process the initial voice input received from the user.
        This method must be implemented by the subclass.
        :param voice_input: The voice input to process.
        """
        pass

    def process_follow_up_input(self, follow_up_input):
        """
        Process a follow-up input during a conversation.
        This method should be overridden by the subclass if it requires handling follow-up conversations.
        :param follow_up_input: The follow-up input to process.
        """
        pass
    
    def request_further_context(self, system_msg, start_conversation=True, context=None):
        """
        Request additional context from the user and start a conversation.
        :param system_msg: The message to prompt the user for more information.
        :param context:  Optional context of the conversation.
        :return: The prompt message to be sent to the user.
        """
        if start_conversation:
            self.start_conversation(context)
        return system_msg


class ExtensionRouter:
    def __init__(self, logger):
        self.log = logger
        self.extensions = []
        self.active_conversation_extension = None
        self.pending_disambiguation = None
        
    def add_extension(self, service):
        if not isinstance(service, AtlasExtension):
            raise TypeError("Service must be an instance of AtlasExtension")
        self.extensions.append(service)
        self.log.debug(f"Added extension: {service.__class__.__name__}")
    
    def route_voice_input(self, voice_input):
        # If there is an active conversation, route input to that extension for follow-up processing
        if self.active_conversation_extension and self.active_conversation_extension.is_in_conversation():
            return self.active_conversation_extension.process_follow_up_input(voice_input)

        if self.pending_disambiguation is not None:
            return self.handle_follow_up(voice_input)

        # If no active conversation, check each extension for potential matches.
        matching_extensions = [extension for extension in self.extensions if extension.can_handle_input(voice_input)]
                    
        if len(matching_extensions) > 1:
            # Ambiguity detected, ask for clarification
            self.log.debug(f"Detected ambiguity. Multiple extensions matched input: {voice_input} {matching_extensions}")
            return self.disambiguate_intent(voice_input, matching_extensions)

        if matching_extensions:
            self.log.debug(f"Detected matching extension: {matching_extensions[0]}. Processing input: {voice_input}")
            response = matching_extensions[0].process_voice_input(voice_input)
                    
            if response:
                # If the extension starts a conversation, set it as active
                if matching_extensions[0].is_in_conversation():
                    self.active_conversation_extension = matching_extensions[0]
                return response

        # End the active conversation if no extension responds
        if self.active_conversation_extension:
            self.active_conversation_extension.end_conversation()
            self.active_conversation_extension = None

        return None

    def handle_voice_input(self, voice_input):
        return self.route_voice_input(voice_input)
    
    def disambiguate_intent(self, voice_input, matching_extensions):
        """
        Ask the user to clarify their intent when multiple extensions match the input.
        :param voice_input: The original voice input from the user.
        :param matching_extensions: List of extensions that matched the input.
        :return: Prompt for the user to clarify their intent.
        """
        # Store the initial input and matching extensions for later processing
        self.pending_disambiguation = {
            "original_input": voice_input,
            "matching_extensions": matching_extensions
        }

        # Generate a prompt based on the types of extensions that matched
        extension_types = [ext.__class__.__name__ for ext in matching_extensions]
        prompt = "Did you mean a " + " or a ".join(extension_types) + "?"
        return prompt
    
    def handle_follow_up(self, user_response):
        """
        Handle the user's response to the disambiguation prompt.
        :param user_response: The user's response to the clarification prompt.
        :return: The response from the appropriate extension.
        """
        if not self.pending_disambiguation:
            return "I'm not sure what you're referring to."

        # Determine which extension to use based on the user's response
        for extension in self.pending_disambiguation["matching_extensions"]:
            if extension.keyword_in_response(user_response):
                # Clear the pending disambiguation as it's no longer needed
                self.pending_disambiguation = None
                return extension.process_voice_input(self.pending_disambiguation["original_input"])

        # If none match, clear the disambiguation and ask for more clarity
        self.pending_disambiguation = None
        return "I'm still not sure what you meant. Could you please specify if it's a movie, game, or something else?"