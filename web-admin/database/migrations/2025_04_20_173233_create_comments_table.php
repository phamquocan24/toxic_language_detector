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
        Schema::create('comments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained();
            $table->text('content');
            $table->string('processed_content')->nullable();
            $table->string('category'); // clean, offensive, hate, spam
            $table->float('confidence_score');
            $table->json('probabilities')->nullable();
            $table->string('platform'); // facebook, youtube, twitter
            $table->string('platform_id')->nullable();
            $table->string('source_url')->nullable();
            $table->string('commenter_name')->nullable();
            $table->json('keywords')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('comments');
    }
};
