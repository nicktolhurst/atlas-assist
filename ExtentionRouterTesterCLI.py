import click
from loguru import logger as log
from atlas.extension_router import AtlasExtension, ExtensionRouter
from atlas.extensions.radarr.ext.radarr_ext import RadarrExtension
from atlas.extensions.radarr.tests.mock_radar_api import mock_radarr_api


def create_router():
    router = ExtensionRouter()
    router.add_extension(RadarrExtension(log, mock_radarr_api))
    return router

@click.command()
def test_router():
    router = create_router()

    while True:
        voice_input = click.prompt('[USR]')
                       
        if voice_input.lower() == 'exit':
            break

        response = router.handle_voice_input(voice_input)
        
        if not response:
            click.echo("No response from extension.")
            continue
            
        click.echo(f"[SYS]: {response}")

if __name__ == '__main__':
    test_router()