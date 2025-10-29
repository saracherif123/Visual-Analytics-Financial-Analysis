#!/usr/bin/env python3
"""
Add a super category column using rule-based logic (fast and reliable).
This avoids API issues and model loading time.
"""

import pandas as pd

def categorize_transaction(description, merchant_category, transaction_type):
    """
    Categorize a transaction into one of 5 high-level super categories.
    """
    desc_lower = str(description).lower()
    category_lower = str(merchant_category).lower()
    type_lower = str(transaction_type).lower()
    
    # 1. INCOME_RECEIPTS - Money coming in
    if type_lower in ['topup', 'reward', 'interest']:
        return 'Income_Receipts'
    
    income_keywords = ['payment from', 'transfer from', 'refund', 'reward', 
                       'interest earned', 'income', 'deposit', 'salary']
    if any(keyword in desc_lower for keyword in income_keywords):
        return 'Income_Receipts'
    
    # 2. FINANCIAL_MANAGEMENT - Banking, transfers, fees
    if type_lower in ['transfer', 'fee']:
        if 'to person_name' in desc_lower or 'from person_name' in desc_lower:
            return 'Financial_Management'
    
    financial_keywords = ['transfer to', 'transfer from', 'to person_name', 
                         'fee', 'delivery', 'account_ref', 'closing', 
                         'pocket withdrawal']
    if any(keyword in desc_lower for keyword in financial_keywords):
        return 'Financial_Management'
    
    if 'financial services' in category_lower:
        return 'Financial_Management'
    
    # 3. ESSENTIAL_LIVING - Basic necessities
    essential_keywords = ['carrefour', 'aldi', 'lidl', 'colruyt', 'food', 
                         'groceries', 'supermarket', 'healthcare', 'pharmacy',
                         'utilities', 'bill', 'orange', 'electric', 'water',
                         'transportation', 'sncb', 'de lijn', 'metro', 'bus',
                         'education', 'university', 'school', 'wash campus']
    
    if any(keyword in desc_lower or keyword in category_lower for keyword in essential_keywords):
        return 'Essential_Living'
    
    if 'utilities & bills' in category_lower:
        return 'Essential_Living'
    
    if 'transportation' in category_lower:
        return 'Essential_Living'
    
    if 'education' in category_lower:
        return 'Essential_Living'
    
    # Essential groceries vs dining
    grocery_stores = ['carrefour', 'aldi', 'lidl', 'colruyt', 'okay', 'condis', 
                     'primaprix', 'norma', 'euroshop', 'action', 'mcdonald',
                     'delhaize', 'continente', 'intermarche', 'hema', 'supermercado',
                     'wenzhou', 'amigo', 'tradys', 'asiatic', 'asian']
    if any(store in desc_lower for store in grocery_stores):
        return 'Essential_Living'
    
    # 4. LIFESTYLE_SPENDING - Non-essential, discretionary spending
    lifestyle_keywords = ['restaurant', 'cafe', 'bar', 'cinema', 'entertainment',
                         'shopping', 'retail', 'amazon', 'netflix', 'streaming',
                         'personal care', 'beauty', 'hobby', 'travel', 'flight',
                         'hotel', 'vacation', 'uber', 'taxi', 'bolt', 'pico',
                         'doner', 'pizza', 'airbnb', 'booking', 'hairdresser',
                         'nail', 'manicure', 'massage', 'spa', 'gym', 'yoga',
                         'coffee', 'chocolate', 'museum', 'theater', 'circus']
    
    if any(keyword in desc_lower or keyword in category_lower for keyword in lifestyle_keywords):
        return 'Lifestyle_Spending'
    
    if 'entertainment' in category_lower or 'shopping & retail' in category_lower:
        return 'Lifestyle_Spending'
    
    if 'personal care' in category_lower:
        return 'Lifestyle_Spending'
    
    # Dining out vs groceries
    restaurants = ['pico', 'doner', 'restaurant', 'atelier', 'theo', 'chez',
                   'cafe', 'bar', 'bakery', 'pastry', 'croissanterie', 'sandwich',
                   'frituur', 'friterie', 'kebab', 'pizza', 'burger', 'hot dog',
                   'tacos', 'sushi', 'chinese', 'indian', 'vietnamese', 'thai',
                   'tapas', 'ramen', 'curry', 'pasta', 'ristorante', 'trattoria']
    if any(place in desc_lower for place in restaurants):
        return 'Lifestyle_Spending'
    
    # 5. OTHER - Default fallback (minimize this!)
    
    # Additional checks to reduce "Other" category
    
    # Card payments that weren't caught above
    if type_lower == 'card payment':
        # Check if it's food-related (likely dining)
        if any(kw in desc_lower for kw in ['food', 'eat', 'dine', 'meal', 'snack']):
            return 'Lifestyle_Spending'
        # Check if it's essential grocery
        if any(kw in desc_lower for kw in ['market', 'store', 'shop', 'superm']):
            return 'Essential_Living'
        # Generic merchants - try to categorize based on description
        if len(desc_lower) < 10:  # Very short descriptions
            return 'Other'
    
    # Generic check for services
    if 'service' in desc_lower or 'servicios' in desc_lower:
        return 'Financial_Management'
    
    return 'Other'

def main():
    # Read the data
    print("Loading data...")
    df = pd.read_csv('financial_data_SaraSaad_final.csv')
    
    print(f"✅ Loaded {len(df)} transactions")
    print("\n🔄 Categorizing transactions with smart rule-based logic...\n")
    
    # Apply categorization
    df['Super_Category'] = df.apply(
        lambda row: categorize_transaction(
            row['Description_Anon'],
            row['Merchant_Category'],
            row['Type']
        ), 
        axis=1
    )
    
    # Save the updated dataset
    output_file = 'financial_data_SaraSaad_final.csv'
    df.to_csv(output_file, index=False)
    
    print(f"💾 Updated dataset saved to '{output_file}'")
    
    # Show distribution
    print("\n📊 Super Category Distribution:")
    dist = df['Super_Category'].value_counts()
    for category, count in dist.items():
        print(f"  {category}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n📋 Dataset now has {len(df.columns)} columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()

