<?php

namespace Database\Seeders;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use Carbon\Carbon;

class UsersTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $now = Carbon::now();

        // Thêm roles trước
        DB::table('roles')->insert([
            [
                'id' => 1,
                'name' => 'admin',
                'description' => 'Administrator with full access',
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'id' => 2,
                'name' => 'user',
                'description' => 'Regular user with limited access',
                'created_at' => $now,
                'updated_at' => $now
            ]
        ]);

        // Thêm users
        DB::table('users')->insert([
            [
                'username' => 'admin',
                'email' => 'admin@example.com',
                'name' => 'Administrator',
                'password' => Hash::make('password'),
                'is_active' => true,
                'is_verified' => true,
                'last_login' => Carbon::parse('2025-05-05 09:42:18'),
                'last_activity' => Carbon::parse('2025-05-05 09:42:18'),
                'role_id' => 1, // Admin
                'created_at' => Carbon::parse('2025-04-13 15:20:58'),
                'updated_at' => Carbon::parse('2025-04-13 15:20:58')
            ],
            [
                'username' => 'hung123',
                'email' => 'anpham25052004@gmail.com',
                'name' => 'annnnn',
                'password' => Hash::make('password2'),
                'is_active' => true,
                'is_verified' => true,
                'last_login' => Carbon::parse('2025-04-13 17:41:13'),
                'last_activity' => Carbon::parse('2025-04-13 17:41:13'),
                'role_id' => 2, // User
                'created_at' => Carbon::parse('2025-04-13 16:06:28'),
                'updated_at' => Carbon::parse('2025-04-13 16:06:28')
            ]
        ]);
    }
}
