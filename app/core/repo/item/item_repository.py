from pydantic import UUID4
from sqlalchemy.orm import Session
import app.models as models
import app.schema as schema
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
import uuid


class ItemRepo:

    def create_item(self, item: schema.Items, db: Session, usr_token: str):
        new_item = models.Items(
            item_name=item.item_name,
            item_description=item.item_description,
            price=item.price,
            available=item.available,
            owner_id=uuid.UUID(usr_token) # convert user id back into a uuid in order for database to understand the relationship
        )

        db.add(new_item)
        db.commit()
        return {"status": 201, "message": "Item created successfully"}

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
            item = db.query(models.Items).filter(models.Items.ItemID == id).first()
            return {
                "name": item.item_name,
                "description": item.item_description,
                "price": item.price,
                "owner": db.query(models.User).filter(models.User.id == item.owner_id).first().username
            }
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Item does not exist")
        except AttributeError:
            raise HTTPException(status_code=404, detail="Item does not exist")
