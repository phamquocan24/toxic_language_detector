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
            $table->text('content');
            $table->text('processed_content')->nullable();
            $table->string('platform', 50)->index();
            $table->string('source_user_name', 255)->nullable()->index();
            $table->text('source_url')->nullable();

            // Kết quả phân loại
            $table->integer('prediction')->index()->comment('0: clean, 1: offensive, 2: hate, 3: spam');
            $table->float('confidence');
            $table->text('probabilities')->nullable()->comment('Xác suất cho từng nhãn dưới dạng JSON');

            // Vector đặc trưng cho tìm kiếm tương tự
            $table->text('vector_representation')->nullable()->comment('Stored as JSON string');

            // Trường hỗ trợ (phục vụ xử lý)
            $table->boolean('is_reviewed')->default(false)->index();
            $table->integer('review_result')->nullable();
            $table->text('review_notes')->nullable();
            $table->timestamp('review_timestamp')->nullable();

            // Khóa ngoại
            $table->unsignedInteger('user_id')->index();
            $table->foreign('user_id')->references('id')->on('users');

            // Metadata bổ sung từ nền tảng
            $table->json('meta_data')->nullable();

            // Để hỗ trợ báo cáo
            $table->boolean('is_in_report')->default(false)->index();
            $table->text('report_ids')->nullable()->comment('Lưu danh sách IDs của báo cáo dưới dạng JSON');

            // Tạo timestamps (created_at, updated_at)
            $table->timestamps();

            // Tạo các indices phức hợp
            $table->index(['platform', 'prediction'], 'idx_comment_platform_prediction');
            $table->index(['created_at', 'prediction'], 'idx_comment_created_prediction');
            $table->index(['user_id', 'platform'], 'idx_comment_user_platform');
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
