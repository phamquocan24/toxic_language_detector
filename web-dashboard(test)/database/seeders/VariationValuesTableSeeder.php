<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Carbon\Carbon;

class VariationValuesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $now = Carbon::now();

        // Size variation values (variation_id = 1)
        DB::table('variation_values')->insert([
            ['variation_id' => 1, 'label' => 'Small', 'value' => 'S', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 1, 'label' => 'Medium', 'value' => 'M', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 1, 'label' => 'Large', 'value' => 'L', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 1, 'label' => 'Extra Large', 'value' => 'XL', 'position' => 4, 'created_at' => $now, 'updated_at' => $now],

            // Color variation values (variation_id = 2)
            ['variation_id' => 2, 'label' => 'Red', 'value' => '#FF0000', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 2, 'label' => 'Blue', 'value' => '#0000FF', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 2, 'label' => 'Green', 'value' => '#00FF00', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 2, 'label' => 'Black', 'value' => '#000000', 'position' => 4, 'created_at' => $now, 'updated_at' => $now],

            // Material variation values (variation_id = 3)
            ['variation_id' => 3, 'label' => 'Cotton', 'value' => 'cotton', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 3, 'label' => 'Polyester', 'value' => 'polyester', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 3, 'label' => 'Leather', 'value' => 'leather', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],

            // Style variation values (variation_id = 4)
            ['variation_id' => 4, 'label' => 'Casual', 'value' => 'casual', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 4, 'label' => 'Formal', 'value' => 'formal', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 4, 'label' => 'Sports', 'value' => 'sports', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],

            // Package variation values (variation_id = 7)
            ['variation_id' => 7, 'label' => 'Single', 'value' => 'single', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 7, 'label' => 'Pair', 'value' => 'pair', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 7, 'label' => 'Box', 'value' => 'box', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],

            // Flavor variation values (variation_id = 8)
            ['variation_id' => 8, 'label' => 'Vanilla', 'value' => 'vanilla', 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 8, 'label' => 'Chocolate', 'value' => 'chocolate', 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['variation_id' => 8, 'label' => 'Strawberry', 'value' => 'strawberry', 'position' => 3, 'created_at' => $now, 'updated_at' => $now],
        ]);
    }
}
