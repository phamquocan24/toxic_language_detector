<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Carbon\Carbon;

class ProductVariantsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $now = Carbon::now();

        DB::table('product_variants')->insert([
            [
                'product_id' => 1,
                'name' => 'Red - Small',
                'price' => 100.0000,
                'special_price' => 10.0000,
                'special_price_type' => 2, // Percent
                'special_price_start' => $now->copy()->subDays(10)->toDateString(),
                'special_price_end' => $now->copy()->addDays(20)->toDateString(),
                'selling_price' => 90.0000,
                'sku' => 'P1-RED-S',
                'manage_stock' => 1,
                'qty' => 100,
                'in_stock' => 1,
                'is_default' => 1,
                'is_active' => 1,
                'position' => 1,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 1,
                'name' => 'Red - Medium',
                'price' => 110.0000,
                'special_price' => 10.0000,
                'special_price_type' => 2, // Percent
                'special_price_start' => $now->copy()->subDays(10)->toDateString(),
                'special_price_end' => $now->copy()->addDays(20)->toDateString(),
                'selling_price' => 99.0000,
                'sku' => 'P1-RED-M',
                'manage_stock' => 1,
                'qty' => 85,
                'in_stock' => 1,
                'is_default' => 0,
                'is_active' => 1,
                'position' => 2,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 1,
                'name' => 'Blue - Small',
                'price' => 100.0000,
                'special_price' => 15.0000,
                'special_price_type' => 1, // Fixed
                'special_price_start' => $now->copy()->subDays(5)->toDateString(),
                'special_price_end' => $now->copy()->addDays(15)->toDateString(),
                'selling_price' => 85.0000,
                'sku' => 'P1-BLUE-S',
                'manage_stock' => 1,
                'qty' => 75,
                'in_stock' => 1,
                'is_default' => 0,
                'is_active' => 1,
                'position' => 3,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 2,
                'name' => 'Cotton - White',
                'price' => 200.0000,
                'special_price' => 20.0000,
                'special_price_type' => 2, // Percent
                'special_price_start' => $now->copy()->subDays(2)->toDateString(),
                'special_price_end' => $now->copy()->addDays(30)->toDateString(),
                'selling_price' => 160.0000,
                'sku' => 'P2-COT-WHT',
                'manage_stock' => 1,
                'qty' => 50,
                'in_stock' => 1,
                'is_default' => 1,
                'is_active' => 1,
                'position' => 1,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 2,
                'name' => 'Polyester - Black',
                'price' => 180.0000,
                'special_price' => 30.0000,
                'special_price_type' => 1, // Fixed
                'special_price_start' => $now->copy()->subDays(15)->toDateString(),
                'special_price_end' => $now->copy()->addDays(5)->toDateString(),
                'selling_price' => 150.0000,
                'sku' => 'P2-POLY-BLK',
                'manage_stock' => 1,
                'qty' => 65,
                'in_stock' => 1,
                'is_default' => 0,
                'is_active' => 1,
                'position' => 2,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 3,
                'name' => 'Standard',
                'price' => 350.0000,
                'special_price' => null,
                'special_price_type' => 1, // Fixed
                'special_price_start' => null,
                'special_price_end' => null,
                'selling_price' => 350.0000,
                'sku' => 'P3-STD',
                'manage_stock' => 0,
                'qty' => null,
                'in_stock' => 1,
                'is_default' => 1,
                'is_active' => 1,
                'position' => 1,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 4,
                'name' => 'Premium Package',
                'price' => 500.0000,
                'special_price' => 50.0000,
                'special_price_type' => 1, // Fixed
                'special_price_start' => $now->copy()->subDays(10)->toDateString(),
                'special_price_end' => $now->copy()->addDays(20)->toDateString(),
                'selling_price' => 450.0000,
                'sku' => 'P4-PREMIUM',
                'manage_stock' => 1,
                'qty' => 20,
                'in_stock' => 1,
                'is_default' => 1,
                'is_active' => 1,
                'position' => 1,
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'product_id' => 4,
                'name' => 'Basic Package',
                'price' => 300.0000,
                'special_price' => 15.0000,
                'special_price_type' => 2, // Percent
                'special_price_start' => $now->copy()->subDays(5)->toDateString(),
                'special_price_end' => $now->copy()->addDays(25)->toDateString(),
                'selling_price' => 255.0000,
                'sku' => 'P4-BASIC',
                'manage_stock' => 1,
                'qty' => 35,
                'in_stock' => 1,
                'is_default' => 0,
                'is_active' => 1,
                'position' => 2,
                'created_at' => $now,
                'updated_at' => $now
            ]
        ]);
    }
}
