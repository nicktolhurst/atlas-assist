import click
from loguru import logger as log
from atlas.extension_router import AtlasExtension, ExtensionRouter
from atlas.extensions.lists.ext.lists_ext import ListExtension


def create_router():
    router = ExtensionRouter(log)
    router.add_extension(ListExtension(log))
    return router

@click.command()
def test_router():
    router = create_router()

    while True:
        voice_input = click.prompt('[USR]')
                       
        if voice_input.lower() == 'exit':
            break

        try:
            response = router.handle_voice_input(voice_input)
        except ValueError as e:
            log.error(e)
            click.echo(f"[SYS]: There was an unexpected error: {e}")
            continue
        
        if not response:
            click.echo("No response from extension.")
            continue
            
        click.echo(f"[SYS]: {response}")

if __name__ == '__main__':
    test_router()