from sqlalchemy.orm import joinedload
from database.db import get_session
from database.models import Listing
from logic.points import calculate_points


def create_listing(seller_id, mode, title, category, size, material, condition,
                   og_price, wear_label, brand_tier,
                   accepts_money, price,
                   swap_type, swap_condition,
                   image_path):
    """
    Create a new listing and pre-compute its points_value.

    Sell mode
    ---------
      accepts_money=True  → buyer can also pay ₹price instead of points
      accepts_money=False → buyer must pay with points

    Swap mode
    ---------
      swap_type="cloth"  → buyer must describe the cloth they're offering
      swap_type="points" → buyer pays points_value points
    """
    db = get_session()
    try:
        pts = calculate_points(
            float(og_price or 0), condition, wear_label, brand_tier
        )
        listing = Listing(
            seller_id=seller_id,
            mode=mode,
            title=title,
            category=category,
            size=size,
            material=material,
            condition=condition,
            og_price=float(og_price or 0),
            wear_label=wear_label,
            brand_tier=brand_tier,
            points_value=pts,
            accepts_money=1 if accepts_money else 0,
            price=float(price or 0) if accepts_money else 0.0,
            swap_type=swap_type,        # "cloth" | "points"
            swap_condition=swap_condition,
            image_path=image_path,
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing
    except Exception as e:
        db.rollback()
        raise e


def browse_listings(mode=None, size=None, category=None, exclude_user_id=None):
    db = get_session()
    query = (
        db.query(Listing)
        .options(joinedload(Listing.seller))
        .filter(Listing.status == "active")
    )
    if mode:
        query = query.filter(Listing.mode == mode)
    if size:
        query = query.filter(Listing.size == size)
    if category:
        query = query.filter(Listing.category == category)
    if exclude_user_id:
        query = query.filter(Listing.seller_id != exclude_user_id)
    results = query.order_by(Listing.created_at.desc()).all()
    for listing in results:
        db.expunge(listing)
    return results


def get_my_listings(user_id):
    db = get_session()
    results = (
        db.query(Listing)
        .options(joinedload(Listing.seller))
        .filter_by(seller_id=user_id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    for listing in results:
        db.expunge(listing)
    return results


def delete_listing(listing_id, user_id):
    db = get_session()
    try:
        listing = db.query(Listing).filter_by(
            id=listing_id, seller_id=user_id
        ).first()
        if listing:
            db.delete(listing)
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False