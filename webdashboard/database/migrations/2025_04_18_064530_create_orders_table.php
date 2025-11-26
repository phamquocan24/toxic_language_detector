<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateOrdersTable extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedBigInteger('customer_id')->nullable();
            $table->string('customer_email')->nullable();
            $table->string('customer_phone')->nullable();
            $table->string('customer_first_name')->nullable();
            $table->string('customer_last_name')->nullable();

            $table->string('billing_first_name')->nullable();
            $table->string('billing_last_name')->nullable();
            $table->string('billing_address_1')->nullable();
            $table->string('billing_address_2')->nullable();
            $table->string('billing_city')->nullable();
            $table->string('billing_state')->nullable();
            $table->string('billing_zip')->nullable();
            $table->string('billing_country')->nullable();

            $table->string('shipping_first_name')->nullable();
            $table->string('shipping_last_name')->nullable();
            $table->string('shipping_address_1')->nullable();
            $table->string('shipping_address_2')->nullable();
            $table->string('shipping_city')->nullable();
            $table->string('shipping_state')->nullable();
            $table->string('shipping_zip')->nullable();
            $table->string('shipping_country')->nullable();

            $table->decimal('sub_total', 18, 4)->default(0);
            $table->string('shipping_method')->nullable();
            $table->decimal('shipping_cost', 18, 4)->default(0);
            $table->unsignedBigInteger('coupon_id')->nullable();
            $table->decimal('discount', 18, 4)->default(0);
            $table->decimal('total', 18, 4)->default(0);
            $table->string('payment_method')->nullable();
            $table->string('currency')->nullable();
            $table->decimal('currency_rate', 18, 4)->default(1);
            $table->string('locale')->nullable();
            $table->string('status')->nullable();
            $table->text('note')->nullable();

            $table->softDeletes();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
}
