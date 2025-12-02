"""
Database event handlers and triggers.

This module defines SQLAlchemy event listeners that automatically update
wine quantities when stock movements are inserted, updated, or deleted.
"""
from sqlalchemy import event

from db.models import Wine, StockMovement


@event.listens_for(StockMovement, "after_insert")
def update_wine_quantity_after_insert(
    mapper, connection, target: StockMovement
) -> None:
    """
    Update wine quantity after a new stock movement is inserted.
    
    Increases quantity for purchases, decreases for sales.
    
    Parameters:
        mapper: SQLAlchemy mapper (for metadata, not used directly)
        connection: Database connection (operates in the flush cycle)
        target: StockMovement instance that triggered the event
    """
    # Calculate new quantity based on transactoin type
    if target.transaction_type == "purchase":
        new_quantity = Wine.quantity + target.quantity
    elif target.transaction_type == "sale":
        new_quantity = Wine.quantity - target.quantity
    else:
        # Edge case: Invalid transaction type
        return
    
    # Update wine table
    connection.execute(
        Wine.__table__.update()
        .where(Wine.id == target.wine_id)
        .values(quantity=new_quantity)
    )


@event.listens_for(StockMovement, "after_delete")
def update_wine_quantity_after_delete(
    mapper, connection, target: StockMovement
) -> None:
    """
    Update wine quantity after a stock movement is deleted.
    
    Reverses the original transaction: decreases quantity for deleted purchases,
    increases for deleted sales.
    
    Parameters:
        mapper: SQLAlchemy mapper (for metadata, not used directly)
        connection: Database connection (operates in the flush cycle)
        target: StockMovement instance that triggered the event
    """
    # Check if it is a purchase or sale
    if target.transaction_type == "purchase":
        new_quantity = Wine.quantity - target.quantity
    elif target.transaction_type == "sale":
        new_quantity = Wine.quantity + target.quantity
    else:
        # Edge case: invalid transaction type
        return
    
    # Update wine table
    connection.execute(
        Wine.__table__.update()
        .where(Wine.id == target.wine_id)
        .values(quantity=new_quantity)
    )

@event.listens_for(StockMovement, "before_update")
def update_wine_quantity_before_update(
    mapper, connection, target: StockMovement
) -> None:
    """
    Update wine quantity before a stock movement is updated.
    
    Calculates the net change by removing the old quantity and adding the new one.
    Handles changes in both quantity and transaction type.
    
    Parameters:
        mapper: SQLAlchemy mapper (for metadata, not used directly)
        connection: Database connection (operates in the flush cycle)
        target: StockMovement instance that triggered the event
    """
    # Get current record from database
    current_record = connection.execute(
        StockMovement.__table__.select().where(StockMovement.id == target.id)
    ).fetchone()

    # Get old and new values
    old_quantity = current_record.quantity
    old_type = current_record.transaction_type
    new_quantity = target.quantity
    new_type = target.transaction_type

    # Skip update if nothing changed
    if old_quantity == new_quantity and old_type == new_type:
        return

    # Calculate net quantity change
    # Step 1: Remove old value
    if old_type == "purchase":
        net_quantity = -old_quantity
    elif old_type == "sale":
        net_quantity = old_quantity
    else:
        # Edge case: invalid transaction type
        net_quantity = 0
    
    # Step 2: Add new value
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
