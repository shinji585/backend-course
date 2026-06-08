import uuid
from datetime import datetime

from app.enums.enum_status import EnumStatus
from app.schemas.create import CreateItem
from app.schemas.detail import DetailItem
from app.schemas.out import OutItem
from app.schemas.update import UpdateItem


class ItemController:
    def __init__(self, repository: list[dict] | None = None) -> None:
        self.repository: list[dict] = repository if repository is not None else []

    def createItem(self, item_in: CreateItem) -> DetailItem:
        item_data = item_in.model_dump()

        item_data["id"] = uuid.uuid4()
        item_data["status"] = EnumStatus.PENDING
        item_data["created_at"] = datetime.now()

        self.repository.append(item_data)

        return DetailItem.model_validate(item_data)

    def listItems(self) -> list[OutItem]:
        return [OutItem.model_validate(_) for _ in self.repository]

    def getItemDetail(self, item_id: uuid.UUID) -> DetailItem | None:
        for item in self.repository:
            if item["id"] == item_id:
                return DetailItem.model_validate(item)
        return None

    def deleteItem(self, item_id: uuid.UUID) -> dict[str, DetailItem] | None:
        for i, item in enumerate(self.repository):
            if item["id"] == item_id:
                item_eliminado = self.repository.pop(i)
                return {"Elemento success eliminated": DetailItem.model_validate(item_eliminado)}
        return None

    def updateItem(self, item_id: uuid.UUID, item_update: UpdateItem) -> DetailItem | None:
        for item in self.repository:
            if item["id"] == item_id:
                update_data = item_update.model_dump(exclude_unset=True)
                item |= update_data
                return DetailItem.model_validate(item)
        return None
