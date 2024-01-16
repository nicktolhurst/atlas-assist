import pytest
from atlas.extension_router import AtlasExtension, ExtensionRouter

class TestAtlasExtension(AtlasExtension):
    def __init__(self):
        super().__init__()
        self.context = {}

    def can_handle_input(self, voice_input):
        return 'test' in voice_input

    def process_voice_input(self, voice_input):
        if 'context' in voice_input:
            self.context['context'] = voice_input.split(' ')[-1]
            return "Context received."
        else:
            return "This is a test."

    def is_context_complete(self):
        return 'context' in self.context

    def prompt_for_missing_context(self):
        return "Missing context."


@pytest.fixture
def router():
    router = ExtensionRouter()
    test_extension = TestAtlasExtension()
    router.add_extension(test_extension)
    return router

def test_add_extension(router):
    test_extension = TestAtlasExtension()
    router.add_extension(test_extension)
    assert test_extension in router.extensions

def test_route_voice_input(router):
    response = router.route_voice_input('test')
    assert response == "This is a test."

def test_handle_voice_input(router):
    response = router.handle_voice_input('test')
    assert response == "This is a test."
    
def test_route_voice_input_no_handler(router):
    response = router.route_voice_input('nonexistent')
    assert response is None
    
def test_handle_voice_input_no_handler(router):
    response = router.handle_voice_input('nonexistent')
    assert response is None

def test_can_handle_input():
    extension = TestAtlasExtension()
    assert extension.can_handle_input('test')
    assert not extension.can_handle_input('nonexistent')
    
def test_is_context_complete():
    extension = TestAtlasExtension()
    router = ExtensionRouter()
    router.add_extension(extension)
    response = router.route_voice_input('test with complete context')
    assert extension.is_context_complete()
    
def test_is_context_complete_without_context():
    extension = TestAtlasExtension()
    router = ExtensionRouter()
    router.add_extension(extension)
    response = router.route_voice_input('test without complete c0nt3xt')
    assert not extension.is_context_complete()
    
def test_prompt_for_missing_context():
    extension = TestAtlasExtension()
    assert extension.prompt_for_missing_context() == "Missing context."