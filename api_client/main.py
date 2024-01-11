import aiofiles
import re
import time
from aiohttp import ClientSession

class ChatResponse:
    def __init__(self, response, logger):
        self.log = logger
        self.response = response
        self.message = self.response["choices"][0]["message"]
        pass

    def as_text(self):
        return self.message["content"]

    def as_chunks(self, max_chunk_size=50):
        text = self.as_text()
        self.log.debug(f'Attempting to chunk: "{text}"')
        sentences = re.split(r"(?<=[.!?]) +", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding the next sentence exceeds max length, add the current chunk to the list
            chunks.append(current_chunk.strip())
            current_chunk = sentence

            # Check for very long sentences and split further at commas or hyphens
            while len(current_chunk) > max_chunk_size:
                sub_chunk, current_chunk = _split_long_sentence(
                    current_chunk, max_chunk_size
                )
                chunks.append(sub_chunk.strip())

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Filter none values
        chunks = list(filter(None, chunks))

        self.log.debug(f"Split response into {len(chunks)} chunks:")
        self.log.debug(f"Chunks: {chunks}")

        return chunks


class APIClient:
    def __init__(self, logger, api_key):
        self.log = logger
        self.api_key = api_key
        self.client_session = None

    async def open_session(self):
        if self.client_session:
            return
        self.client_session = ClientSession()
        self.log.debug("API Client initialized.")

    async def close_session(self):
        if self.client_session:
            await self.client_session.close()

    async def v1_chat_completions_async(
        self, messages, model="gpt-4-vision-preview", max_tokens=500, n=1, temperature=1
    ):
        async with self.client_session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "n": n,
                "temperature": temperature,
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
        ) as response:
            if response.status == 200:
                response = await response.json()
                self.log.debug(response)
                return ChatResponse(response, self.log)
            elif response.status == 400:
                self.log.error(
                    f"STATUS: {response.status} - Invalid request parameters.\n{await response.text()}"
                )
            else:
                self.log.error(
                    f"STATUS: {response.status} - OpenAI API request failed with response\n{await response.text()}"
                )
                return None

    async def v1_audio_speech_async(
        self, chunky_text, model="tts-1", voice="echo", response_format="mp3"
    ):
        for chunk in chunky_text:
            input = {
                "model": model,
                "input": chunk,
                "voice": voice,
                "response_format": response_format,
            }
            async with self.client_session.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=input,
            ) as response:
                if response.status == 200:
                    file_path = f'.tmp/speech-{time.strftime("%Y%m%d-%H%M%S")}.mp3'
                    # Download the speech file
                    async with aiofiles.open(file_path, "wb") as file:
                        await file.write(await response.read())

                    yield file_path
                elif response.status == 400:
                    self.log.error(
                        f"STATUS: {response.status} - Invalid request parameters:\n{await response.text()}\nRequest Parameters:\n{input}"
                    )
                else:
                    self.log.error(
                        f"STATUS: {response.status} - OpenAI API request failed with response\n{await response.text()}"
                    )


def _split_long_sentence(sentence, max_length):
    """
    Splits a long sentence at the last comma or hyphen before the max_length.
    """
    # Find the last comma or hyphen before max_length
    split_point = max(
        sentence.rfind(",", 0, max_length),
        sentence.rfind("-", 0, max_length)
        # sentence.rfind(" ", 0, max_length),
    )

    return sentence[:split_point], sentence[split_point + 1 :]
