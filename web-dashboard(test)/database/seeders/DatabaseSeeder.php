<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;


class DatabaseSeeder extends Seeder
{
    public function run()
    {
        $this->call([
            BrandsTableSeeder::class,
            CategoriesTableSeeder::class,
            VariationsTableSeeder::class,
            VariationValuesTableSeeder::class,
            ProductsTableSeeder::class,
            ProductCategoriesTableSeeder::class,
            ProductVariantsSeeder::class,
            ProductVariationsTableSeeder::class,
            UsersTableSeeder::class,
        ]);
    }
}
