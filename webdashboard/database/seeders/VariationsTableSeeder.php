<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Carbon\Carbon;

class VariationsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $now = Carbon::now();

        DB::table('variations')->insert([
            ['name' => 'Size', 'type' => 'dropdown', 'is_global' => 1, 'position' => 1, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Color', 'type' => 'color', 'is_global' => 1, 'position' => 2, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Material', 'type' => 'dropdown', 'is_global' => 1, 'position' => 3, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Style', 'type' => 'dropdown', 'is_global' => 1, 'position' => 4, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Weight', 'type' => 'text', 'is_global' => 1, 'position' => 5, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Dimension', 'type' => 'text', 'is_global' => 1, 'position' => 6, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Package', 'type' => 'dropdown', 'is_global' => 1, 'position' => 7, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Flavor', 'type' => 'dropdown', 'is_global' => 1, 'position' => 8, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Volume', 'type' => 'text', 'is_global' => 1, 'position' => 9, 'created_at' => $now, 'updated_at' => $now],
            ['name' => 'Pattern', 'type' => 'dropdown', 'is_global' => 1, 'position' => 10, 'created_at' => $now, 'updated_at' => $now],
        ]);
    }
}
