<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Tạo roles
        $adminRole = Role::create(['name' => 'admin']);
        $userRole = Role::create(['name' => 'user']);
        
        // Tạo permissions
        $permissions = [
            'view dashboard',
            'manage users',
            'manage comments',
            'export data',
            'view own comments',
        ];
        
        foreach ($permissions as $permission) {
            Permission::create(['name' => $permission]);
        }
        
        // Gán permissions cho roles
        $adminRole->givePermissionTo(Permission::all());
        $userRole->givePermissionTo(['view own comments']);
        
        // Tạo tài khoản admin
        $admin = User::create([
            'name' => 'Admin',
            'email' => 'admin@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now()
        ]);
        
        $admin->assignRole('admin');
        
        // Tạo tài khoản user demo
        $user = User::create([
            'name' => 'User Demo',
            'email' => 'user@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now()
        ]);
        
        $user->assignRole('user');
    }
}
