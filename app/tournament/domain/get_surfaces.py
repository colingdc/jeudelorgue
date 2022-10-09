from ...models import Surface


def get_surfaces():
    return Surface.get_all_surfaces()
