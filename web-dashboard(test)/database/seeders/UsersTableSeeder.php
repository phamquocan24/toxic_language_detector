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

        DB::table('users')->insert([
            [
                'first_name' => 'John',
                'last_name' => 'Doe',
                'email' => 'john.doe@example.com',
                'password' => Hash::make('password1'),
                'email_verified_at' => $now,
                'role' => 1, // Admin
                'last_login' => '2025-01-01 00:00:00',
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'first_name' => 'Jane',
                'last_name' => 'Doe',
                'email' => 'jane.doe@example.com',
                'password' => Hash::make('password2'),
                'email_verified_at' => $now,
                'role' => 2, // Member
                'last_login' => '2025-01-02 00:00:00',
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'first_name' => 'Alice',
                'last_name' => 'Smith',
                'email' => 'alice.smith@example.com',
                'password' => Hash::make('password3'),
                'email_verified_at' => $now,
                'role' => 2, // Member
                'last_login' => '2025-01-03 00:00:00',
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'first_name' => 'Bob',
                'last_name' => 'Johnson',
                'email' => 'bob.johnson@example.com',
                'password' => Hash::make('password4'),
                'email_verified_at' => $now,
                'role' => 2, // Member
                'last_login' => '2025-01-04 00:00:00',
                'created_at' => $now,
                'updated_at' => $now
            ],
            [
                'first_name' => 'Charlie',
                'last_name' => 'Brown',
                'email' => 'charlie.brown@example.com',
                'password' => Hash::make('password5'),
                'email_verified_at' => $now,
                'role' => 2, // Member
                'last_login' => '2025-01-05 00:00:00',
                'created_at' => $now,
                'updated_at' => $now
            ]
        ]);
    }
}
