from database.db_example import get_session
from database.models import Review, Match, Listing


def submit_review(match_id, reviewer_id, seller_id, rating, comment=""):
    """Submit a 1-5 star review after a completed transaction."""
    db = get_session()
    try:
        if db.query(Review).filter_by(match_id=match_id).first():
            return False, "You already reviewed this transaction"
        match = db.query(Match).get(match_id)
        if not match or match.status != "completed":
            return False, "Transaction must be completed before reviewing"
        if not (1 <= rating <= 5):
            return False, "Rating must be between 1 and 5"
        review = Review(
            match_id=match_id,
            reviewer_id=reviewer_id,
            seller_id=seller_id,
            rating=rating,
            comment=comment,
        )
        db.add(review)
        db.commit()
        return True, "Review submitted!"
    except Exception as e:
        db.rollback()
        return False, str(e)


def get_seller_reviews(seller_id):
    """Return all reviews for a seller with avg rating."""
    db = get_session()
    reviews = db.query(Review).filter_by(seller_id=seller_id).all()
    for r in reviews:
        db.expunge(r)
    avg = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
    return reviews, avg


def get_review_for_match(match_id):
    db = get_session()
    r = db.query(Review).filter_by(match_id=match_id).first()
    if r:
        db.expunge(r)
    return r