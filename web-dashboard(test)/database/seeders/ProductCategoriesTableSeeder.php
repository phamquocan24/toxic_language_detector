<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ProductCategoriesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Mỗi sản phẩm có thể thuộc nhiều danh mục
        DB::table('product_categories')->insert([
            // Sản phẩm 1 thuộc 2 danh mục
            ['product_id' => 1, 'category_id' => 1],
            ['product_id' => 1, 'category_id' => 2],

            // Sản phẩm 2 thuộc 2 danh mục
            ['product_id' => 2, 'category_id' => 1],
            ['product_id' => 2, 'category_id' => 3],

            // Sản phẩm 3 thuộc 1 danh mục
            ['product_id' => 3, 'category_id' => 2],

            // Sản phẩm 4 thuộc 2 danh mục
            ['product_id' => 4, 'category_id' => 3],
            ['product_id' => 4, 'category_id' => 4],

            // Sản phẩm 5 thuộc 1 danh mục
            ['product_id' => 5, 'category_id' => 5],

            // Sản phẩm 6 thuộc 3 danh mục
            ['product_id' => 6, 'category_id' => 1],
            ['product_id' => 6, 'category_id' => 2],
            ['product_id' => 6, 'category_id' => 3],

            // Sản phẩm 7 thuộc 1 danh mục
            ['product_id' => 7, 'category_id' => 4],

            // Sản phẩm 8 thuộc 2 danh mục
            ['product_id' => 8, 'category_id' => 4],
            ['product_id' => 8, 'category_id' => 5],

            // Sản phẩm 9 thuộc 1 danh mục
            ['product_id' => 9, 'category_id' => 5],

            // Sản phẩm 10 thuộc 2 danh mục
            ['product_id' => 10, 'category_id' => 1],
            ['product_id' => 10, 'category_id' => 5]
        ]);
    }
}
