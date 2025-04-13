<?php

if (!function_exists('product_price_formatted')) {

    function product_price_formatted($price): string
    {
        return number_format($price, 0, ',', '.') . 'đ';
    }
}

