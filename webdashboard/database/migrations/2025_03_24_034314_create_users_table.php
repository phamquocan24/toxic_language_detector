<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->increments('id');
            $table->string('username', 50)->unique()->index();
            $table->string('email', 100)->unique()->index();
            $table->string('name', 100)->nullable(); // Tên hiển thị
            $table->string('password');
            $table->boolean('is_active')->default(true)->index();
            $table->boolean('is_verified')->default(false)->index(); // Email đã xác thực chưa

            // Trường cho quản lý phiên
            $table->timestamp('last_login')->nullable();
            $table->timestamp('last_activity')->nullable();
            $table->string('last_login_ip', 45)->nullable(); // Hỗ trợ cả IPv6

            // Trường cho đặt lại mật khẩu
            $table->string('reset_token', 255)->nullable()->unique();
            $table->timestamp('reset_token_expires')->nullable();

            // Trường cho xác thực email
            $table->string('verification_token', 255)->nullable()->unique();
            $table->timestamp('verification_token_expires')->nullable();

            // Cài đặt người dùng
            $table->json('extension_settings')->nullable(); // Cài đặt extension
            $table->json('ui_settings')->nullable(); // Cài đặt giao diện người dùng
            $table->json('notification_settings')->nullable(); // Cài đặt thông báo

            // Thông tin cá nhân bổ sung
            $table->string('avatar_url', 255)->nullable();
            $table->text('bio')->nullable(); // Giới thiệu ngắn

            // Role (Foreign key)
            $table->integer('role_id')->unsigned()->nullable();

            $table->rememberToken();
            $table->timestamps();
            $table->softDeletes();
        });

        // Tạo bảng roles nếu chưa có
        if (!Schema::hasTable('roles')) {
            Schema::create('roles', function (Blueprint $table) {
                $table->increments('id');
                $table->string('name', 50)->unique();
                $table->string('description')->nullable();
                $table->timestamps();
            });

            // Thêm khóa ngoại sau khi tạo bảng roles
            Schema::table('users', function (Blueprint $table) {
                $table->foreign('role_id')->references('id')->on('roles');
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('users');
        Schema::dropIfExists('roles');
    }
};
