def render_all(entities, surface):
    for entity in entities:
        if entity is not None and hasattr(entity, "draw"):
            entity.draw(surface)


def update_all(entities, **kwargs):
    for entity in entities:
        if entity is not None and hasattr(entity, "update"):
            entity.update(**kwargs)
