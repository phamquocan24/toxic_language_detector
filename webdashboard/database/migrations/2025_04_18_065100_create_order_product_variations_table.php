<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateOrderProductVariationsTable extends Migration
{
    public function up()
    {
        Schema::create('order_product_variations', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('order_product_id');
            $table->unsignedInteger('variation_id');
            $table->string('type', 191);
            $table->string('value', 191);
            $table->timestamps();

            $table->foreign('order_product_id')->references('id')->on('order_products')->onDelete('cascade');
            $table->foreign('variation_id')->references('id')->on('variations')->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('order_product_variations');
    }
}
