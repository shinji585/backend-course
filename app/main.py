from pathlib import Path

from app.services.tags import TagsServices

if __name__ == "__main__":
    data_path = Path(__file__).absolute().parent / "db" / "data" / "tagsData.json"

    object_value = TagsServices(config_path=data_path)

    print(object_value.add_tag())
