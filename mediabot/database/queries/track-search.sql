SELECT * FROM tracks WHERE query ILIKE :query ORDER BY created_at DESC LIMIT 20;
