/*
    This SQL query retrieves order information from the Magento database.
    It selects the increment ID, customer ID, SKU, quantity ordered, name, base grand total, and row total for each order item.
    The query joins the sales_order_item table with the sales_order table using the order_id and entity_id columns respectively.
    The result is ordered by the entity_id in descending order.
*/
select
    `order`.increment_id,
    `order`.customer_id,
    `order_items`.sku,
    `order_items`.qty_ordered,
    `order_items`.name,
    `order`.base_grand_total,
    `order_items`.row_total
from
    sales_order_item as `order_items`
    left join sales_order as `order` on `order`.entity_id = `order_items`.order_id
order by
    `order`.entity_id DESC