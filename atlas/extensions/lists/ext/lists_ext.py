from atlas.extension_router import AtlasExtension
from .lists_ctx import Context
from .lists_store import Store


ITEM_NOT_FOUND__SYS_MSG = "Tell the user that the item is not found in list. Do not respond with anything else."
LIST_NOT_FOUND__SYS_MSG = "Tell the user that the list was not found. Do not respond with anything else."
LIST_ALREADY_EXISTS__SYS_MSG = "Tell the user that the list already exists. Do not respond with anything else."
LIST_CREATED__SYS_MSG = "Tell the user that the list has been created. Do not respond with anything else."
LIST_REMOVED__SYS_MSG = "Tell the user that the list has been removed. Do not respond with anything else."
ITEM_ADDED__SYS_MSG = "Tell the user that the item has been added to the list. Do not respond with anything else."
ITEM_REMOVED__SYS_MSG = "Tell the user that the item has been removed from the list. Do not respond with anything else."

class ListExtension(AtlasExtension):
    def __init__(self, logger):
        super().__init__()
        self.log = logger
        self.store = Store(logger) # loads on initialization, but can also be called with self.store.load()
        self.context = Context(logger)
        self.conversation_state = {}

    """
    Used by the extension router to determine whether this extension can handle 
    the given voice input. 
    """  
    def can_handle_input(self, voice_input):
        return any(word in voice_input for word in ['list', 'lists'])

    def process_voice_input(self, voice_input):
        self.context.extract_from_input(voice_input)

        if not self.context.action:
            raise ValueError("No action found in context.")
        
        if not self.context.list:
            raise ValueError("No list found in context.")
        
        if not self.context.item and self.context.action in ['add', 'remove']:
            raise ValueError("No item found in context.")
        
        if self.context.action == 'read':
            if self.context.list in self.store.lists:
                return f"Read back the user the items in the list: {self.store.lists[self.context.list]}"
            else:
                return f"Tell the user they don't have a '{self.context.list}' list."
        
        if self.context.action:
            self.log.debug(f"Handling context: {self.context.__dict__}")
            SYS_MSG = self._handle_request()
            self.context = Context(self.log); # reset context
            return SYS_MSG
            
    def process_follow_up_input(self, follow_up_input):
        pass

    def _handle_request(self):
        if self.context.action == 'add': 
            return self.add_item(self.context.list, self.context.item)
        
        if self.context.action == 'remove':
            return self.remove_item(self.context.list, self.context.item)
        
        if self.context.action == 'create':
            return self.create_list(self.context.list)
        
        if self.context.action == 'delete':
            return self.remove_list(self.context.list)
        
             
    def add_item(self, list, item):
        if list in self.store.lists:
            self.store.lists[list].append(item)
            self.store.save()
            return ITEM_ADDED__SYS_MSG
        else:
            return LIST_NOT_FOUND__SYS_MSG


    def remove_item(self, list, item):
        if list in self.store.lists:
            if item in self.store.lists[list]:
                self.store.lists[list].remove(item)
                self.store.save()
                return ITEM_REMOVED__SYS_MSG
            else:
                return ITEM_NOT_FOUND__SYS_MSG
        else:
            return LIST_NOT_FOUND__SYS_MSG

    def create_list(self, list):
        if list in self.store.lists:
            return LIST_ALREADY_EXISTS__SYS_MSG
        else:
            self.store.lists[list] = []
            self.store.save()
            return LIST_CREATED__SYS_MSG

    def remove_list(self, list):
        if list in self.store.lists:
            del self.store.lists[list]
            self.store.save()
            return LIST_REMOVED__SYS_MSG
        else:
            return LIST_NOT_FOUND__SYS_MSG