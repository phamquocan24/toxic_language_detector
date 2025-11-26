<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class CategoriesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run()
    {
        DB::table('categories')->insert([
            ['parent_id' => null, 'name' => 'Category 1', 'position' => 1, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 2', 'position' => 2, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 3', 'position' => 3, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 4', 'position' => 4, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 5', 'position' => 5, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 6', 'position' => 6, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 7', 'position' => 7, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 8', 'position' => 8, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 9', 'position' => 9, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
            ['parent_id' => null, 'name' => 'Category 10', 'position' => 10, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()],
        ]);
    }
}
