import uuid

from app.items.schemas import CreateItem, DetailItem, OutItem, UpdateItem


class ItemServices:
    repository: list[DetailItem] = []

    def createItem(self, item_in: CreateItem) -> OutItem:
        item_data = item_in.model_dump()

        detail_item = DetailItem.model_validate(item_data)
        self.repository.append(detail_item)

        return OutItem.model_validate(detail_item)

    def listItems(self, offset: int, limit: int) -> list[OutItem]:
        return [OutItem.model_validate(_) for _ in self.repository[offset:limit]]

    def getItemDetail(self, item_id: uuid.UUID) -> DetailItem | None:
        for item in self.repository:
            if item.id == item_id:
                return DetailItem.model_validate(item)
        return None

    def deleteItem(self, item_id: uuid.UUID) -> dict[str, OutItem] | None:
        for i, item in enumerate(self.repository):
            if item.id == item_id:
                item_eliminado = self.repository.pop(i)
                return {"Element success eliminated": OutItem.model_validate(item_eliminado)}
        return None

    def updateItem(self, item_id: uuid.UUID, item_update: UpdateItem) -> OutItem | None:
        for item in self.repository:
            if item.id == item_id:
                update_data = item_update.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(item, field, value)
                return OutItem.model_validate(item)
        return None
