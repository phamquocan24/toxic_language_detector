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
        Schema::create('products', function (Blueprint $table) {
            $table->increments('id');
            $table->integer('brand_id')->unsigned()->nullable();
            $table->string('name');
            $table->longText('description')->nullable();
            $table->text('short_description')->nullable();
            $table->decimal('price', 18, 4)->unsigned();
            $table->decimal('special_price', 18, 4)->unsigned()->nullable();
            $table->integer('special_price_type')->unsigned()->default(1)->comment('1:Fixed 2:Percent');
            $table->date('special_price_start')->nullable();
            $table->date('special_price_end')->nullable();
            $table->decimal('selling_price', 18, 4)->unsigned()->nullable()->comment('percent = price - (special_price / 100) * price, fixed = price - special_price');
            $table->string('sku')->nullable();
            $table->boolean('manage_stock')->default(0)->comment("0:Don't Track Inventory, 1:Track Inventory");
            $table->integer('qty')->nullable();
            $table->boolean('in_stock')->default(1);
            $table->boolean('is_active')->default(1);
            $table->timestamp('new_from')->nullable();
            $table->timestamp('new_to')->nullable();
            $table->softDeletes();
            $table->timestamps();

            $table->foreign('brand_id')->references('id')->on('brands')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::disableForeignKeyConstraints();
        Schema::dropIfExists('products');
    }
};
