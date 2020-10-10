from fb_scraper import save_to_db, delete_all, ban_urls, delete_data, get_listings_from_db





if __name__ == "__main__":
    listings = get_listings_from_db('SELECT * FROM listings', 'mac_mini.db')
    print('Number of listings saved currently: ', len(listings))
    for i in listings:
        print('\n\n', i)
    listings = get_listings_from_db('SELECT * FROM price_change', 'mac_mini.db')
    for i in listings:
        print('\n\n', i)
    print('Number of price changes saved currently: ', len(listings)) 