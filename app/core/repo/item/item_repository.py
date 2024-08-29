from sqlalchemy.orm import Session
import app.models as models
import app.schema as schema
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException


class ItemRepo:

    def create_item(self, item: schema.Items, db: Session, usr_token: str):
        new_item = models.Items(
            item_name=item.item_name,
            item_description=item.item_description,
            price=item.price,
            available=item.available,
            owner_id=usr_token
        )

        db.add(new_item)
        db.commit()

    def get_item(self, db: Session, id):
        """
        Retrieves an item from the database by its id.

        Args:
            db (Session): The database session.
            id: The id of the item to retrieve.

        Returns:
            A dictionary containing the item's name, description, price, and owner's username.

        Raises:
            HTTPException: If the item does not exist.
        """
        try:
            item = db.query(models.Item).filter(models.Item.id == id).first()
            return {
                "name": item.item_name,
                "description": item.item_description,
                "price": item.price,
                "owner": db.query(models.User).filter(models.User.id == item.owner_id).first().username
            }
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Item does not exist")
