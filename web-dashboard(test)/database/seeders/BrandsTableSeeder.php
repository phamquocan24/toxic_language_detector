<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Carbon\Carbon;

class BrandsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $now = Carbon::now();

        DB::table('brands')->insert([
            ['name' => 'Brand 1', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 2', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 3', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 4', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 5', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 6', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 7', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 8', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 9', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Brand 10', 'is_active' => 1, 'created_at' => $now, 'updated_at' => $now],
        ]);
    }
}
