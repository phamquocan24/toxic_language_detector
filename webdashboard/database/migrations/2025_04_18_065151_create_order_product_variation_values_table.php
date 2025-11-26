<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateOrderProductVariationValuesTable extends Migration
{
    public function up()
    {
        Schema::create('order_product_variation_values', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('order_product_variation_id');
            $table->unsignedInteger('variation_value_id');

            $table->unique(['order_product_variation_id', 'variation_value_id'], 'opv_variation_unique');

            $table->foreign('order_product_variation_id', 'fk_opv_opv_id')
                ->references('id')
                ->on('order_product_variations')
                ->onDelete('cascade');

            $table->foreign('variation_value_id', 'fk_opv_vv_id')
                ->references('id')
                ->on('variation_values')
                ->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('order_product_variation_values');
    }
}
