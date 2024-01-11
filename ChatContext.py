import time


CONTEXT_PRELOAD = [
    {
        "role": "user",
        "content": "You can call me Nick. \
                    I want to refer to you as the Atlas. \
                    Speak to me as if you were Jarvis from Iron Man \
                        but do not reference Jarvis or Iron Man. \
                    Keep responses on short and on point.",
    },
    {"role": "assistant", "content": "Ok"},
]

CHAT_INITIATION_WORDS = ["atlas"]


class Role:
    USER = "user"
    ASSISTANT = "assistant"


class Chat:
    def __init__(self, logger):
        self.context = CONTEXT_PRELOAD
        self.context_preload_length = len(CONTEXT_PRELOAD)
        self.log = logger
        pass

    def get_context(self):
        return self.context, len(self.context)

    def add_msg(self, role, msg):
        self.context.append({"role": role, "content": msg})

    async def initiated(self, listener, loop):
        msg = await listener.listen_async(loop)

        if msg is None:
            return False, None, None

        in_conversation, start_time = start_conversation_when(
            CHAT_INITIATION_WORDS, in_first=3, words_of=msg
        )
        return in_conversation, msg, start_time


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
