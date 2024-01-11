import asyncio
import time
import traceback
from mixer import Mixer
from api_client import APIClient
from listener import Listener
from chat_context import Chat, Role
from loguru import logger as log
import os
import dotenv

dotenv.load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


@log.catch
async def main_async():
    client = APIClient(log, OPENAI_API_KEY)
    listener = Listener(log)
    listener.start_listening()
    chat = Chat(log)
    mixer = Mixer(log)

    async def _graceful_termination():
        # Stop the mixer playing on the executor thread.
        mixer.stop_auto_play_loop()
        # Wait for executor thread to stop.
        await asyncio.wrap_future(executor)
        # Close the API client.
        await client.close_session()

    try:
        await client.open_session()

        loop = asyncio.get_running_loop()
        executor = loop.run_in_executor(None, mixer.start_auto_play_loop)

        # Main Loop
        while True:
            msg, event_id = listener.get_speech_event()

            if msg:
                log.debug(f"Processing speech event: '{event_id}'")
                listener.pause_listening()

                chat.add_msg(Role.USER, msg)

                response = await client.v1_chat_completions_async(chat.context)
                log.info(f"Responding with: '{response.as_text()}'")

                chunks = response.as_chunks()

                clip_gen = client.v1_audio_speech_async(chunks)

                async for clip in clip_gen:
                    mixer.add_clip(clip)

                await mixer.wait_for_finish()
                log.debug(f"Finished processing event: '{event_id}'")
                listener.resume_listening()

    except KeyboardInterrupt:
        log.warning("KeyboardInterrupt. Attempting to terminate gracefully...")
        await _graceful_termination()

    except Exception as e:
        tb = e.__traceback__
        last_call_stack = traceback.extract_tb(tb)[-2]
        log.error(f"EXCEPTION─┐")
        log.error(f"          ├ERROR:  {e}")
        log.error(f"          ├─FILE:   {last_call_stack.filename}")
        log.error(f"          ├─LINE:   {last_call_stack.lineno}")
        log.error(f"          └─FUNC:   {last_call_stack.name}()")
        log.error("Attempting to terminate gracefully...")
        await _graceful_termination()

    finally:
        # Any final cleanup
        log.success("Program terminated gracefully.")


if __name__ == "__main__":
    asyncio.run(main_async())
