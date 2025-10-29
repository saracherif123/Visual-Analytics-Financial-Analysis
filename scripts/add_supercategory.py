#!/usr/bin/env python3
"""
Add a super category column to financial data with 5 high-level categories
using an LLM for automatic categorization.
"""

import pandas as pd
import os
from openai import OpenAI

# Initialize OpenAI client (use environment variable)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def categorize_transaction(description, merchant_category, transaction_type):
    """
    Categorize a transaction into one of 5 high-level super categories.
    """
    prompt = f"""Categorize this financial transaction into ONE of these 5 categories:
1. Essential_Living (housing, utilities, basic groceries, healthcare, transportation)
2. Lifestyle_Spending (dining out, entertainment, shopping, personal care, hobbies)
3. Financial_Management (transfers, investments, savings, fees, financial services)
4. Income_Receipts (salary, payments received, refunds, rewards)
5. Other (anything that doesn't fit above)

Transaction details:
- Description: {description}
- Current Category: {merchant_category}
- Type: {transaction_type}

Respond with ONLY the category name (e.g., "Essential_Living" or "Financial_Management").
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use a cheaper, faster model
            messages=[
                {"role": "system", "content": "You are a financial transaction categorization assistant. Always respond with only the category name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistency
            max_tokens=50
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validate the response
        valid_categories = ['Essential_Living', 'Lifestyle_Spending', 'Financial_Management', 'Income_Receipts', 'Other']
        if category in valid_categories:
            return category
        else:
            print(f"Warning: Invalid category '{category}', defaulting to 'Other'")
            return 'Other'
            
    except Exception as e:
        print(f"Error categorizing transaction: {e}")
        return 'Other'

def main():
    # Read the data
    df = pd.read_csv('financial_data_SaraSaad_final.csv')
    
    print(f"Loaded {len(df)} transactions")
    print("\nProcessing transactions...")
    
    # Add new column with super categories
    # For efficiency, only process unique combinations first
    print("Step 1: Creating unique combinations to reduce API calls...")
    df['unique_key'] = df['Description_Anon'].astype(str) + '|' + \
                      df['Merchant_Category'].astype(str) + '|' + \
                      df['Type'].astype(str)
    
    unique_mapping = {}
    unique_rows = df[['Description_Anon', 'Merchant_Category', 'Type', 'unique_key']].drop_duplicates()
    
    print(f"Step 2: Categorizing {len(unique_rows)} unique transaction patterns...")
    for idx, row in unique_rows.iterrows():
        if idx % 10 == 0:
            print(f"  Processed {idx}/{len(unique_rows)}...")
        
        category = categorize_transaction(
            row['Description_Anon'],
            row['Merchant_Category'],
            row['Type']
        )
        unique_mapping[row['unique_key']] = category
    
    print("\nStep 3: Applying categories to all transactions...")
    df['Super_Category'] = df['unique_key'].map(unique_mapping)
    df = df.drop('unique_key', axis=1)
    
    # Save the updated dataset
    output_file = 'financial_data_SaraSaad_final.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Updated dataset saved to {output_file}")
    
    # Show distribution
    print("\n📊 Super Category Distribution:")
    print(df['Super_Category'].value_counts())
    
    print(f"\n📋 Dataset now has {len(df.columns)} columns:")
    print(list(df.columns))

if __name__ == "__main__":
    main()


