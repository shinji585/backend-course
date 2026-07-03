import json
from pathlib import Path
from typing import Any

from app.schemas.tags import InternalTag
from app.schemas.tracked import TrackedProductCreate, TrackedProductInternal
from app.schemas.tracked.public import TrackedProductPublic


class TrackedProductServices:
    def __init__(self, file_path: str = "data") -> None:
        self.trackedProductData: Any | list[dict] = self.__load_data__(
            file_path=file_path, json_name="trackedProduct.json"
        )
        self.tagsData: Any | list[Any] = self.__load_data__(file_path=file_path, json_name="tags.json")

    def __load_data__(self, file_path: str, json_name: str) -> Any | list[Any]:
        path = Path(__file__).resolve().parents[1] / "db" / file_path / json_name
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and path.stat().st_size > 0:
            with path.open(mode="r", encoding="utf-8") as file:
                return json.load(file)

        with path.open(mode="w", encoding="utf-8") as file:
            json.dump([], file, indent=4)
        return []

    def add_new_trackedProduct(self, product: TrackedProductCreate):
        if product.tags_name is None:
            # create and save the internal tag
            tag_data = InternalTag()
            # after call and create the internal data I save that data
            self.tagsData.append(tag_data)

            # then pass the tag data to the product data
            product_data = product.model_dump(exclude={"tags_name"})
            product_data["tags_id"] = [tag_data.id]
            internal_data = TrackedProductInternal(**product_data)
            internal_data.owner_id = None
            internal_data.current_price = None
            internal_data.updated_at = None

            # save the tracked product
            self.trackedProductData.append(internal_data.model_dump())

            # then return the public model
            for _, tag in enumerate(self.tagsData):
                if tag["id"] in [tag_id for tag_id in internal_data.tags_id]:
                    return TrackedProductPublic.model_validate(tag)
