<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        Schema::create('invitation_tokens', function (Blueprint $table) {
            $table->id();
            $table->string('email')->index();
            $table->string('token');
            $table->integer('role')->default(1); // 1 for admin
            $table->timestamp('created_at')->nullable();
            $table->timestamp('expires_at')->nullable();
            $table->timestamp('accepted_at')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('invitation_tokens');
    }
};
