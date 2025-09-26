from sqlalchemy import event, inspect

from db.models import Wine, StockMovement


@event.listens_for(StockMovement, "after_insert")
def update_wine_quantity(mapper, connection, target):
    """
    Updates the quantity of Wine table after there is an INSERT for StockMovement.
    Parameters:
        mapper: only used for metadata
        connection: Operates in the flush cycle
        target: Instance of the model that triggered the event
    """
    # Check if it is a purchase or sale
    if target.transaction_type == "purchase":
        new_quantity = Wine.quantity + target.quantity
    elif target.transaction_type == "sale":
        new_quantity = Wine.quantity - target.quantity
    # Update wine table
    connection.execute(
        Wine.__table__.update()
        .where(Wine.id == target.wine_id)
        .values(quantity=new_quantity)
    )

@event.listens_for(StockMovement, "after_delete")
def update_wine_quantity(mapper, connection, target):
    """
    Updates the quantity of Wine table after there is a DELETE for StockMovement.
    Parameters:
        mapper: only used for metadata
        connection: Operates in the flush cycle
        target: Instance of the model that triggered the event
    """
    # Check if it is a purchase or sale
    if target.transaction_type == "purchase":
        new_quantity = Wine.quantity - target.quantity
    elif target.transaction_type == "sale":
        new_quantity = Wine.quantity + target.quantity
    # Update wine table
    connection.execute(
        Wine.__table__.update()
        .where(Wine.id == target.wine_id)
        .values(quantity=new_quantity)
    )

@event.listens_for(StockMovement, "before_update")
def update_wine_quantity(mapper, connection, target):
    """
    Updates the quantity of Wine table after there is an UPDATE for StockMovement.
    Parameters:
        mapper: only used for metadata
        connection: Operates in the flush cycle
        target: Instance of the model that triggered the event
    """
    # Start history of the target
    state = inspect(target)

    current_record = connection.execute(
        StockMovement.__table__.select().where(StockMovement.id == target.id)
    ).fetchone()

    # Get old values
    old_quantity = current_record.quantity
    old_type = current_record.transaction_type

    # Get new values
    new_quantity = target.quantity
    new_type = target.transaction_type

    # Stop function if there is no change
    if old_quantity == new_quantity and old_type == new_type:
        return

    # Remove old value
    if old_type == "purchase":
        net_quantity = -old_quantity
    elif old_type == "sale":
        net_quantity = old_quantity
    # Add new value
    if new_type == "purchase":
        net_quantity += new_quantity 
    elif new_type == "sale":
        net_quantity -= new_quantity

    # Update wine table
    connection.execute(
        Wine.__table__.update()
        .where(Wine.id == target.wine_id)
        .values(quantity=Wine.quantity + net_quantity)
    )
