<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateOrderProductsTable extends Migration
{
    public function up(): void
    {
        Schema::create('order_products', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('order_id');
            $table->unsignedInteger('product_id');
            $table->unsignedInteger('product_variant_id')->nullable();
            $table->decimal('unit_price', 18, 4)->default(0);
            $table->integer('qty')->default(1);
            $table->decimal('line_total', 18, 4)->default(0);

            $table->foreign('order_id')->references('id')->on('orders')->onDelete('cascade');
            $table->foreign('product_id')->references('id')->on('products')->onDelete('cascade');
            $table->foreign('product_variant_id')->references('id')->on('product_variants')->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('order_products');
    }
}
