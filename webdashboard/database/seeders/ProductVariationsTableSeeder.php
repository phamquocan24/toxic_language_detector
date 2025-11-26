<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ProductVariationsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run()
    {
        DB::table('product_variations')->insert([
            // Product 1 variations
            ['product_id' => 1, 'variation_id' => 1],
            ['product_id' => 1, 'variation_id' => 2],
            ['product_id' => 1, 'variation_id' => 3],

            // Product 2 variations
            ['product_id' => 2, 'variation_id' => 1],
            ['product_id' => 2, 'variation_id' => 2],
            ['product_id' => 2, 'variation_id' => 4],

            // Product 3 variations
            ['product_id' => 3, 'variation_id' => 2],
            ['product_id' => 3, 'variation_id' => 3],
            ['product_id' => 3, 'variation_id' => 5],

            // Product 4 variations
            ['product_id' => 4, 'variation_id' => 1],
            ['product_id' => 4, 'variation_id' => 4],
            ['product_id' => 4, 'variation_id' => 5],

            // Product 5 variations
            ['product_id' => 5, 'variation_id' => 2],
            ['product_id' => 5, 'variation_id' => 3],
            ['product_id' => 5, 'variation_id' => 4],

            // Product 6 variations
            ['product_id' => 6, 'variation_id' => 3],
            ['product_id' => 6, 'variation_id' => 4],
            ['product_id' => 6, 'variation_id' => 5],

            // Product 7 variations
            ['product_id' => 7, 'variation_id' => 1],
            ['product_id' => 7, 'variation_id' => 2],
            ['product_id' => 7, 'variation_id' => 5],

            // Product 8 variations
            ['product_id' => 8, 'variation_id' => 2],
            ['product_id' => 8, 'variation_id' => 3],
            ['product_id' => 8, 'variation_id' => 4],

            // Product 9 variations
            ['product_id' => 9, 'variation_id' => 1],
            ['product_id' => 9, 'variation_id' => 3],
            ['product_id' => 9, 'variation_id' => 5],

            // Product 10 variations
            ['product_id' => 10, 'variation_id' => 2],
            ['product_id' => 10, 'variation_id' => 4],
            ['product_id' => 10, 'variation_id' => 5],
        ]);
    }
}
