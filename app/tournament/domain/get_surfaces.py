from ...models import Surface


def get_surfaces():
    return [
        (surface.id, surface.name)
        for surface in Surface.query.order_by(Surface.name).all()
    ]
