"""
Script to update all cached offers from USD to INR
Run this once to migrate existing data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.cached_offer import CachedOffer

def update_currency_to_inr():
    """Update all USD offers to INR"""
    db = SessionLocal()
    try:
        # Find all offers with USD currency
        usd_offers = db.query(CachedOffer).filter(CachedOffer.currency == 'USD').all()
        
        print(f"Found {len(usd_offers)} offers with USD currency")
        
        if usd_offers:
            # Convert each offer
            for offer in usd_offers:
                old_price = offer.price
                offer.price = offer.price * 83  # Convert USD to INR (1 USD ≈ 83 INR)
                offer.currency = "INR"
                print(f"Updated offer {offer.offer_id}: ${old_price:.2f} USD → ₹{offer.price:.2f} INR")
            
            db.commit()
            print(f"\n✅ Successfully updated {len(usd_offers)} offers to INR")
        else:
            print("✅ No USD offers found - all offers are already in INR")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating offers: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_currency_to_inr()

