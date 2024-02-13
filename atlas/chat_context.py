import json, os, time

CHAT_INITIATION_WORDS = ["atlas"]


class Role:
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


class Chat:
    def __init__(self, logger):
        self.store_path = f"{os.path.dirname(os.path.abspath(__file__))}/chat_history.json"
        self.log = logger
        CONTEXT_PRELOAD = self.get_context_preload()
        self.context = self.load() or CONTEXT_PRELOAD
        self.context_preload_length = len(CONTEXT_PRELOAD)
        
    def save(self):
        with open(self.store_path, 'w') as f:
            json.dump(self.context, f, indent=4)
        self.log.debug(f"Saved lists to {self.store_path}")

    def load(self):
        if os.path.exists(self.store_path):
            with open(self.store_path, 'r') as f:
                self.log.debug(f"Loaded chat history from {self.store_path}")
                return json.load(f)
        else:
            self.log.warning(f"Chat history file not found at {self.store_path}. Creating new chat history.")
            
    def get_context(self):
        return self.context, len(self.context)

    def add_msg(self, role, msg):
        context = {"role": role, "content": msg}
        self.context.append(context)
        self.save()

    async def initiated(self, listener, loop):
        msg = await listener.listen_async(loop)

        if msg is None:
            return False, None, None

        in_conversation, start_time = start_conversation_when(
            CHAT_INITIATION_WORDS, in_first=3, words_of=msg
        )
        return in_conversation, msg, start_time

    def get_context_preload(self, preload_path="context_preload"):
        try:
            with open(preload_path, "r") as file:
                content = file.read()
        except FileNotFoundError:
            self.log.warn(
                f"The context preload file '{preload_path}' does not exist. \
                    Using empty context. Create a file at '{preload_path} and \
                    add in any context you would like the assistant to be aware \
                    of at startup."
            )

        self.log.debug("Initializing chat...")
        return (
            [
                {"role": "user", "content": content},
                {"role": "assistant", "content": "Ok"},
            ]
            if content
            else []
        )


def start_conversation_when(word_list, in_first, words_of):
    # Split the input string into words
    input_string = words_of
    words = input_string.lower().split()
    start_time = time.time()

    # Check if the string has at least one word
    if len(words) == 0:
        return False, start_time

    # Check if the 'n' word is in the list (if there is a n word..)
    for n in range(in_first - 1):
        if len(words) > n and words[n] in word_list:
            return True, start_time

    return False, start_time
