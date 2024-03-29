import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dotenv
import asyncio
import traceback
from loguru import logger as log
from memory_profiler import profile


from atlas.audio_mixer import Mixer
from atlas.openai_api_client import APIClient
from atlas.listener import Listener
from atlas.chat_context import Chat, Role
from atlas.extension_router import AtlasExtension, ExtensionRouter
from atlas.extensions.radarr.ext.radarr_ext import RadarrExtension
from atlas.extensions.weather.ext.weather_ext import WeatherExtension
from atlas.extensions.lists.ext.lists_ext import ListExtension

# Add this module to path

async def _initialize_deps(api_client, chat, listener, mixer):
    # Initialize API Client
    try:
        api_client = await api_client.open_session()
    except Exception as e:
        log.error(f"Failed to initialize API client: {e}")

    # Initialize Chat Context
    try:
        pass
    except Exception as e:
        log.error(f"Failed to initialize chat context: {e}")

    # Initialize Listener
    try:
        listener = listener.start_listening()
    except Exception as e:
        log.error(f"Failed to initialize listener: {e}")

    # Initialize Mixer
    try:
        mixer.init_mixer(log)
    except Exception as e:
        log.error(f"Failed to initialize Mixer: {e}")

    return api_client, chat, listener, mixer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@log.catch
async def main_async():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print(sys.path)
    
    
    #######################
    # CONFIGURE UTILITIES #
    #######################
    dotenv.load_dotenv()
    log.add("output", rotation="10 MB")
    
    ##################
    # ADD EXTENSIONS #
    ##################
    
    router = ExtensionRouter(log)
    router.add_extension(WeatherExtension(log))
    router.add_extension(RadarrExtension(log))
    router.add_extension(ListExtension(log))

    ##########################
    # SERVICE INITIALIZATION #
    ##########################
    api_client, chat, listener, mixer = await _initialize_deps(
        APIClient(log), Chat(log), Listener(log), Mixer(log)
    )

    # start mixer and listener background services
    loop = asyncio.get_running_loop()
    mixer_ftr = loop.run_in_executor(None, mixer.start_auto_play_loop)

    #########################
    # LOCAL SCOPE FUNCTIONS #
    #########################
    async def _graceful_termination():
        mixer.stop_auto_play_loop()
        await asyncio.wrap_future(mixer_ftr)
        await api_client.close_session()

    #######################
    # MAIN LOOP EXECUTION #
    #######################
    try:
        # Main Loop
        while True:
            msg, event_id = listener.get_speech_event()
            
            if msg:
                log.debug(f"Processing speech event: '{event_id}'")
                listener.pause_listening()
                
                chat.add_msg(Role.USER, msg)
                
                # Run extension middleware
                handled_msg = router.handle_voice_input(msg)
                
                if handled_msg:
                    log.debug(f'HANDLED MSG: {handled_msg}')
                    chat.add_msg(Role.SYSTEM, handled_msg)

                response = await api_client.v1_chat_completions_async(chat.context)
                log.info(f"Responding with: '{response.as_text()}'")
                chat.add_msg(Role.ASSISTANT, response.as_text())

                chunks = response.as_chunks()
                clip_gen = api_client.v1_audio_speech_async(chunks)

                async for clip in clip_gen:
                    mixer.add_clip(clip)
                    
                mixer.wait_for_finish()
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
        raise e

    finally:
        log.success("Program terminated gracefully.")


# Script Execution
if __name__ == "__main__":
    asyncio.run(main_async())


# Package Execution
def main():
    asyncio.run(main_async())
