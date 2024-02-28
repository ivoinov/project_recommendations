/* Adjust SQL mode for the current session to avoid ONLY_FULL_GROUP_BY restrictions */
SET SESSION sql_mode = (SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));

/* Start of the main SELECT query */
select sku,
       -- Use COALESCE to select the first non-null value for product name from store-specific or default
       COALESCE(`store_name`.value, `default_name`.value)   as `product_name`,
       -- Use COALESCE to select the first non-null value for short description from store-specific or default
       COALESCE(`store_short_description`.value, `default_short_description`.value) as `short_description`,
       -- Use COALESCE to select the first non-null value for description from store-specific or default
       COALESCE(`store_description`.value, `default_description`.value) as `description`,
       -- Use COALESCE to select the first non-null value for price from store-specific or default
       COALESCE(`store_price`.value, `default_price`.value) as `price`,
       -- Concatenate all category names for each product, ordered by category ID
       GROUP_CONCAT(COALESCE(`store_category_name`.value, `default_category_name`.value)
               ORDER BY `products_category`.category_id ASC) as `categories`

-- From the main product entity table
from catalog_product_entity as `cpe`

     -- LEFT JOINs to fetch store-specific and default product names
     left join catalog_product_entity_varchar as `store_name`
               on `store_name`.row_id = `cpe`.row_id and `store_name`.store_id = 4 and `store_name`.attribute_id = 73
     left join catalog_product_entity_varchar as `default_name`
               on `default_name`.row_id = `cpe`.row_id and `default_name`.store_id = 0 and `default_name`.attribute_id = 73

     -- LEFT JOINs to fetch store-specific and default short descriptions
     left join catalog_product_entity_text as `store_short_description`
               on `store_short_description`.row_id = `cpe`.row_id and `store_short_description`.store_id = 4 and `store_short_description`.attribute_id = 76
     left join catalog_product_entity_text as `default_short_description`
               on `default_short_description`.row_id = `cpe`.row_id and `default_short_description`.store_id = 0 and `default_short_description`.attribute_id = 76

     -- LEFT JOINs to fetch store-specific and default descriptions
     left join catalog_product_entity_text as `store_description`
               on `store_description`.row_id = `cpe`.row_id and `store_description`.store_id = 4 and `store_description`.attribute_id = 75
     left join catalog_product_entity_text as `default_description`
               on `default_description`.row_id = `cpe`.row_id and `default_description`.store_id = 0 and `default_description`.attribute_id = 75

     -- LEFT JOINs to fetch store-specific and default prices
     left join catalog_product_entity_decimal as `store_price`
               on `store_price`.row_id = `cpe`.row_id and `store_price`.store_id = 4 and `store_price`.attribute_id = 77
     left join catalog_product_entity_decimal as `default_price`
               on `default_price`.row_id = `cpe`.row_id and `default_price`.store_id = 0 and `default_price`.attribute_id = 77

     -- LEFT JOIN to associate products with their categories
     left join catalog_category_product as `products_category`
               on `products_category`.product_id = `cpe`.row_id

     -- LEFT JOINs to fetch store-specific and default category names
     left join catalog_category_entity_varchar as `store_category_name`
               on `store_category_name`.row_id = `products_category`.category_id and `store_category_name`.store_id = 4 and `store_category_name`.attribute_id = 45
     left join catalog_category_entity_varchar as `default_category_name`
               on `default_category_name`.row_id = `products_category`.category_id and `default_category_name`.store_id = 0 and `default_category_name`.attribute_id = 45

-- Group the results by product SKU to ensure unique entries for each product
group by cpe.sku;
