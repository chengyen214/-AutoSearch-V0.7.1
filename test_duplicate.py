from utils.duplicate import (
    is_duplicate,
    save_document
)


id = "abc123"


print(
    is_duplicate(id)
)


save_document(id)


print(
    is_duplicate(id)
)