<?php

return [
    'title' => 'Dashboard',
    'total_sales' => 'Total Sales',
    'total_orders' => 'Total Brands',
    'total_products' => 'Total Products',
    'total_customers' => 'Total Users',

    // Key cho biểu đồ giá sản phẩm
    'product_price_chart' => [
        'title' => 'Product Price Comparison',
    ],

    // Key cho sản phẩm mới nhất
    'latest_products' => [
        'title' => 'Latest Products',
        'name' => 'Product Name',
        'sku' => 'SKU',
        'price' => 'Price',
        'is_active' => 'Status'
    ],

    // Key cho thương hiệu mới nhất
    'latest_brands' => [
        'title' => 'Latest Brands',
        'name' => 'Brand Name',
        'qty' => 'Products',
        'is_active' => 'Status',
    ],

    // Key cho người dùng mới nhất
    'latest_users' => [
        'title' => 'Latest Users',
        'name' => 'User Name',
        'email' => 'Email',
        'role' => 'Role',
    ],

    // Giữ lại các key cũ cho khả năng tương thích
    'dashboard' => 'Dashboard',
    'no_data' => 'No data available!',
    'latest_searches' => [
        'title' => 'Latest Searches',
        'keyword' => 'Keyword',
        'results' => 'Results',
        'hits' => 'Hits',
    ],
    'latest_orders' => [
        'title' => 'Latest Orders',
        'order_id' => 'Order ID',
        'customer' => 'Customer',
        'status' => 'Status',
        'total' => 'Total',
    ],
    'latest_reviews' => [
        'title' => 'Latest Reviews',
        'product' => 'Product',
        'customer' => 'Customer',
        'rating' => 'Rating',
    ],
    'sales_analytics' => [
        'title' => 'Sales Analytics',
        'orders' => 'Orders',
        'sales' => 'Sales',
    ],
];
