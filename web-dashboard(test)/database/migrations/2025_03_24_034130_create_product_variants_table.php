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
        Schema::create('product_variants', function (Blueprint $table) {
            $table->increments('id');
            $table->integer('product_id')->unsigned();
            $table->string('name');
            $table->decimal('price', 18, 4)->unsigned()->nullable();
            $table->decimal('special_price', 18, 4)->unsigned()->nullable();
            $table->integer('special_price_type')->unsigned()->default(1)->comment('1:Fixed 2:Percent');
            $table->date('special_price_start')->nullable();
            $table->date('special_price_end')->nullable();
            $table->decimal('selling_price', 18, 4)->unsigned()->nullable()->comment('percent = price - (special_price / 100) * price, fixed = price - special_price');
            $table->string('sku')->nullable();
            $table->boolean('manage_stock')->default(0)->comment("0:Don't Track Inventory, 1:Track Inventory");
            $table->integer('qty')->nullable();
            $table->boolean('in_stock')->nullable();
            $table->boolean('is_default')->nullable();
            $table->boolean('is_active')->nullable();
            $table->integer('position')->unsigned()->nullable();
            $table->softDeletes();
            $table->timestamps();

            $table->foreign('product_id')->references('id')->on('products')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::disableForeignKeyConstraints();
        Schema::dropIfExists('product_variants');
    }
};
