@extends('admin::layout')

@section('title', trans('admin::dashboard.title'))

@section('content_header')
    <h3>{{ trans('admin::dashboard.title') }}</h3>
@endsection

@section('content')
    <div class="dashboard-container">
        <!-- Stats Cards Row -->
        <div class="grid clearfix">
            <div class="row">
                <div class="col-lg-3 col-md-6 col-sm-6">
                    <div class="single-grid total-sales">
                        <div>
                            <span class="count" id="total-sales">71.09K</span>
                            <span class="title">{{ trans('admin::dashboard.total_sales') }}</span>
                        </div>
                        <div class="single-grid-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" id="Outline" viewBox="0 0 512 512" width="512" height="512">
                                <path d="M488,144H440a8,8,0,0,0-8,8V456a8,8,0,0,0,8,8h48a8,8,0,0,0,8-8V152A8,8,0,0,0,488,144Zm-8,304H448V160h32Z"></path>
                                <path d="M408,464a8,8,0,0,0,8-8V216a8,8,0,0,0-8-8H360a8,8,0,0,0-8,8V456a8,8,0,0,0,8,8ZM368,224h32V448H368Z"></path>
                                <path d="M328,464a8,8,0,0,0,8-8V272a8,8,0,0,0-8-8H280a8,8,0,0,0-8,8V456a8,8,0,0,0,8,8ZM288,280h32V448H288Z"></path>
                                <path d="M248,464a8,8,0,0,0,8-8V336a8,8,0,0,0-8-8H200a8,8,0,0,0-8,8V456a8,8,0,0,0,8,8ZM208,344h32V448H208Z"></path>
                                <path d="M168,464a8,8,0,0,0,8-8V368a8,8,0,0,0-8-8H120a8,8,0,0,0-8,8v88a8,8,0,0,0,8,8Zm-40-88h32v72H128Z"></path>
                                <path d="M88,464a8,8,0,0,0,8-8V408a8,8,0,0,0-8-8H40a8,8,0,0,0-8,8v48a8,8,0,0,0,8,8ZM48,416H80v32H48Z"></path>
                                <path d="M216,144h16a8,8,0,0,0,0-16h-8v-8a8,8,0,0,0-16,0v9.376A24,24,0,0,0,216,176a8,8,0,0,1,0,16H200a8,8,0,0,0,0,16h8v8a8,8,0,0,0,16,0v-9.376A24,24,0,0,0,216,160a8,8,0,0,1,0-16Z"></path>
                                <path d="M488,48H440a8,8,0,0,0,0,16h28.686l-112,112H311.664c.219-2.639.336-5.306.336-8a96,96,0,1,0-113.677,94.362L164.687,296H104a8,8,0,0,0-5.657,2.343l-80,80a8,8,0,0,0,11.314,11.314L107.313,312H168a8,8,0,0,0,5.657-2.343l45.723-45.723A96.19,96.19,0,0,0,308.963,192H360a8,8,0,0,0,5.657-2.343L480,75.314V104a8,8,0,0,0,16,0V56A8,8,0,0,0,488,48ZM216,248a80,80,0,1,1,80-80A80.091,80.091,0,0,1,216,248Z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-6">
                    <div class="single-grid total-orders">
                        <div>
                            <span class="count" id="total-orders">46</span>
                            <span class="title">{{ trans('admin::dashboard.total_orders') }}</span>
                        </div>
                        <div class="single-grid-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12.85 17.81">
                                <g id="Layer_2" data-name="Layer 2">
                                    <g id="Layer_1-2" data-name="Layer 1">
                                        <path d="M12.77,2.27,10.58.08a.3.3,0,0,0-.2-.08H.29A.29.29,0,0,0,0,.29V17.52a.29.29,0,0,0,.29.29H12.57a.28.28,0,0,0,.28-.29v-15A.32.32,0,0,0,12.77,2.27Zm-.49,15H.57V.57h9.52V2.48a.28.28,0,0,0,.29.28h.84a.28.28,0,0,0,.28-.28.29.29,0,0,0-.28-.29h-.56V1L12.28,2.6Zm-1.2-6.43a.28.28,0,0,1-.28.28H2.06a.29.29,0,1,1,0-.57H10.8A.28.28,0,0,1,11.08,10.81ZM1.77,12.33a.28.28,0,0,1,.29-.28H6.43a.27.27,0,0,1,.28.28.28.28,0,0,1-.28.29H2.06A.29.29,0,0,1,1.77,12.33Zm9.31,1.53a.28.28,0,0,1-.28.29h-.3a.29.29,0,0,1,0-.58h.3A.28.28,0,0,1,11.08,13.86Zm-1.41,0a.29.29,0,0,1-.29.29H2.06a.29.29,0,1,1,0-.58H9.38A.29.29,0,0,1,9.67,13.86Zm-3,1.53a.28.28,0,0,1-.28.29H2.06a.29.29,0,1,1,0-.58H6.43A.28.28,0,0,1,6.71,15.39ZM4.65,8.71a.29.29,0,0,0,0-.58H2.24V2.31H4.05V4.15a.29.29,0,0,0,.47.23l.64-.52.64.52A.28.28,0,0,0,6,4.44l.12,0a.29.29,0,0,0,.16-.26V3.09A.28.28,0,0,0,6,2.8a.29.29,0,0,0-.29.29v.47l-.35-.29a.3.3,0,0,0-.36,0l-.36.29V2.31H8.07V5.73a2,2,0,0,0-.56-.08A1.91,1.91,0,1,0,8.65,6V2a.29.29,0,0,0-.29-.29H2A.29.29,0,0,0,1.67,2v6.4A.29.29,0,0,0,2,8.71Zm2.86.2A1.34,1.34,0,1,1,8.86,7.57,1.34,1.34,0,0,1,7.51,8.91ZM8.35,7a.29.29,0,0,1,0,.41l-.84.92a.32.32,0,0,1-.22.1.23.23,0,0,1-.17-.07L6.7,8a.29.29,0,1,1,.35-.45l.23.18L7.94,7A.3.3,0,0,1,8.35,7Z"></path>
                                    </g>
                                </g>
                            </svg>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-6">
                    <div class="single-grid total-products">
                        <div>
                            <span class="count" id="total-products">140</span>
                            <span class="title">{{ trans('admin::dashboard.total_products') }}</span>
                        </div>
                        <div class="single-grid-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" id="Capa_1" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">
                                <g><g> <path d="M491.729,112.971L259.261,0.745c-2.061-0.994-4.461-0.994-6.521,0L20.271,112.971c-2.592,1.251-4.239,3.876-4.239,6.754    v272.549c0,2.878,1.647,5.503,4.239,6.754l232.468,112.226c1.03,0.497,2.146,0.746,3.261,0.746s2.23-0.249,3.261-0.746    l232.468-112.226c2.592-1.251,4.239-3.876,4.239-6.754V119.726C495.968,116.846,494.32,114.223,491.729,112.971z M256,15.828    l215.217,103.897l-62.387,30.118c-0.395-0.301-0.812-0.579-1.27-0.8L193.805,45.853L256,15.828z M176.867,54.333l214.904,103.746    l-44.015,21.249L132.941,75.624L176.867,54.333z M396.799,172.307v78.546l-41.113,19.848v-78.546L396.799,172.307z     M480.968,387.568L263.5,492.55V236.658l51.873-25.042c3.73-1.801,5.294-6.284,3.493-10.015    c-1.801-3.729-6.284-5.295-10.015-3.493L256,223.623l-20.796-10.04c-3.731-1.803-8.214-0.237-10.015,3.493    c-1.801,3.73-0.237,8.214,3.493,10.015l19.818,9.567V492.55L31.032,387.566V131.674l165.6,79.945    c1.051,0.508,2.162,0.748,3.255,0.748c2.788,0,5.466-1.562,6.759-4.241c1.801-3.73,0.237-8.214-3.493-10.015l-162.37-78.386    l74.505-35.968L340.582,192.52c0.033,0.046,0.07,0.087,0.104,0.132v89.999c0,2.581,1.327,4.98,3.513,6.353    c1.214,0.762,2.599,1.147,3.988,1.147c1.112,0,2.227-0.247,3.26-0.746l56.113-27.089c2.592-1.251,4.239-3.875,4.239-6.754v-90.495    l69.169-33.392V387.568z"></path></g></g>
                                <g><g><path d="M92.926,358.479L58.811,342.01c-3.732-1.803-8.214-0.237-10.015,3.493c-1.801,3.73-0.237,8.214,3.493,10.015    l34.115,16.469c1.051,0.508,2.162,0.748,3.255,0.748c2.788,0,5.466-1.562,6.759-4.241    C98.22,364.763,96.656,360.281,92.926,358.479z"></path></g></g>
                                <g><g><path d="M124.323,338.042l-65.465-31.604c-3.731-1.801-8.214-0.237-10.015,3.494c-1.8,3.73-0.236,8.214,3.494,10.015    l65.465,31.604c1.051,0.507,2.162,0.748,3.255,0.748c2.788,0,5.466-1.562,6.759-4.241    C129.617,344.326,128.053,339.842,124.323,338.042z"></path></g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g>
                            </svg>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 col-sm-6">
                    <div class="single-grid total-customers">
                        <div>
                            <span class="count" id="total-customers">4</span>
                            <span class="title">{{ trans('admin::dashboard.total_customers') }}</span>
                        </div>
                        <div class="single-grid-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" height="496pt" viewBox="0 -72 496 496" width="496pt">
                                <path d="m98.113281 168.125c-31.730469 0-57.542969-25.578125-57.542969-57.007812 0-31.433594 25.8125-57.011719 57.542969-57.011719 31.726563 0 57.535157 25.574219 57.535157 57.011719 0 31.433593-25.808594 57.007812-57.535157 57.007812zm0-98.019531c-22.910156 0-41.542969 18.398437-41.542969 41.011719 0 22.609374 18.632813 41.007812 41.542969 41.007812 22.902344 0 41.535157-18.398438 41.535157-41.007812 0-22.613282-18.632813-41.011719-41.535157-41.011719zm0 0"></path>
                                <path d="m121.261719 325.96875h-100.351563c-11.53125 0-20.910156-9.320312-20.910156-20.777344v-26.167968c0-53.570313 44.011719-97.15625 98.113281-97.15625 21.277344 0 41.53125 6.640624 58.554688 19.199218 3.554687 2.625 4.3125 7.632813 1.6875 11.191406-2.625 3.550782-7.628907 4.308594-11.1875 1.6875-14.253907-10.515624-31.214844-16.078124-49.054688-16.078124-45.277343 0-82.113281 36.410156-82.113281 81.15625v26.167968c0 2.632813 2.203125 4.777344 4.910156 4.777344h100.355469c4.414063 0 8 3.582031 8 8 0 4.414062-3.585937 8-8.003906 8zm0 0"></path>
                                <path d="m475.089844 319.914062h-100.351563c-4.414062 0-8-3.582031-8-8 0-4.414062 3.585938-8 8-8h100.355469c2.707031 0 4.910156-2.140624 4.910156-4.773437v-26.167969c0-44.753906-36.835937-81.15625-82.113281-81.15625-18.910156 0-37.371094 6.511719-51.984375 18.339844-3.429688 2.777344-8.464844 2.25-11.25-1.183594-2.777344-3.433594-2.253906-8.472656 1.1875-11.253906 17.449219-14.121094 39.484375-21.902344 62.046875-21.902344 54.097656 0 98.109375 43.582032 98.109375 97.15625v26.167969c0 11.453125-9.378906 20.773437-20.910156 20.773437zm0 0"></path>
                                <path d="m397.886719 164.171875c-31.726563 0-57.535157-25.574219-57.535157-57.007813 0-31.433593 25.808594-57.011718 57.535157-57.011718 31.730469 0 57.542969 25.574218 57.542969 57.011718s-25.816407 57.007813-57.542969 57.007813zm0-98.019531c-22.902344 0-41.535157 18.398437-41.535157 41.011718 0 22.613282 18.632813 41.007813 41.535157 41.007813 22.910156 0 41.542969-18.394531 41.542969-41.007813 0-22.613281-18.636719-41.011718-41.542969-41.011718zm0 0"></path><path d="m356.578125 352h-217.15625c-14.425781 0-26.160156-11.648438-26.160156-25.96875v-36.804688c0-73.554687 60.4375-133.394531 134.738281-133.394531s134.738281 59.839844 134.738281 133.394531v36.804688c0 14.320312-11.734375 25.96875-26.160156 25.96875zm-108.578125-180.164062c-65.472656 0-118.738281 52.664062-118.738281 117.394531v36.804687c0 5.496094 4.558593 9.96875 10.160156 9.96875h217.152344c5.601562 0 10.160156-4.472656 10.160156-9.96875v-36.804687c.003906-64.730469-53.261719-117.394531-118.734375-117.394531zm0 0"></path>
                                <path d="m245.21875 146.484375c-40.765625 0-73.9375-32.855469-73.9375-73.246094 0-40.386719 33.167969-73.238281 73.9375-73.238281 40.773438 0 73.941406 32.855469 73.941406 73.242188 0 40.390624-33.171875 73.242187-73.941406 73.242187zm0-130.484375c-31.945312 0-57.9375 25.679688-57.9375 57.242188 0 31.566406 25.992188 57.246093 57.9375 57.246093 31.949219 0 57.941406-25.679687 57.941406-57.246093 0-31.5625-25.992187-57.242188-57.941406-57.242188zm0 0"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Product Prices Chart and Latest Brands Section -->
        <div class="row mt-4">
            <!-- Product Prices Chart -->
            <div class="col-md-8">
                <div class="box product-price-chart">
                    <div class="box-header with-border">
                        <h3 class="box-title">{{ trans('admin::dashboard.product_price_chart.title') }}</h3>
                    </div>
                    <div class="box-body">
                        <canvas class="chart" style="height: 300px;"></canvas>
                    </div>
                </div>
            </div>

            <!-- Latest Brands -->
            <div class="col-md-4">
                <div class="box">
                    <div class="box-header with-border">
                        <h3 class="box-title">{{ trans('admin::dashboard.latest_brands.title') }}</h3>
                    </div>
                    <div class="box-body">
                        <div class="table-responsive">
                            <table id="latest-brands-table" class="table table-borderless">
                                <thead>
                                    <tr class="brands-header">
                                        <th>{{ trans('admin::dashboard.latest_brands.name') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_brands.qty') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_brands.is_active') }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td colspan="3" class="text-center no-data">Loading brands...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Latest Products and Latest Users Section -->
        <div class="row mt-4">
            <!-- Latest Products -->
            <div class="col-md-8">
                <div class="box">
                    <div class="box-header with-border">
                        <h3 class="box-title">{{ trans('admin::dashboard.latest_products.title') }}</h3>
                    </div>
                    <div class="box-body">
                        <div class="table-responsive">
                            <table id="latest-products-table" class="table table-borderless">
                                <thead>
                                    <tr class="products-header">
                                        <th>{{ trans('admin::dashboard.latest_products.name') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_products.sku') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_products.price') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_products.is_active') }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td colspan="4" class="text-center no-data">Loading products...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Latest Users -->
            <div class="col-md-4">
                <div class="box">
                    <div class="box-header with-border">
                        <h3 class="box-title">{{ trans('admin::dashboard.latest_users.title') }}</h3>
                    </div>
                    <div class="box-body">
                        <div class="table-responsive">
                            <table id="latest-users-table" class="table table-borderless">
                                <thead>
                                    <tr class="users-header">
                                        <th>{{ trans('admin::dashboard.latest_users.name') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_users.email') }}</th>
                                        <th>{{ trans('admin::dashboard.latest_users.role') }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td colspan="3" class="text-center no-data">Loading users...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
           </div>
        </div>
    </div>
@endsection

@push('styles')
<style>
    .dashboard-container {
        padding: 15px;
    }
    .stats-cards {
        margin-bottom: 20px;
    }

    /* Grid mới */
    .grid {
        margin-bottom: 30px;
    }

    .single-grid {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        background-color: white;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .single-grid:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }

    .single-grid .count {
        display: block;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
        color: #333;
    }

    .single-grid .title {
        display: block;
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .single-grid-icon {
        width: 55px;
        height: 55px;
        background-color: rgba(0,0,0,0.04);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .single-grid-icon svg {
        width: 28px;
        height: 28px;
        fill: #666;
    }

    .total-sales .single-grid-icon {
        background-color: rgba(33, 150, 243, 0.1);
    }

    .total-sales .single-grid-icon svg {
        fill: #2196F3;
    }

    .total-orders .single-grid-icon {
        background-color: rgba(233, 30, 99, 0.1);
    }

    .total-orders .single-grid-icon svg {
        fill: #E91E63;
    }

    .total-products .single-grid-icon {
        background-color: rgba(255, 152, 0, 0.1);
    }

    .total-products .single-grid-icon svg {
        fill: #FF9800;
    }

    .total-customers .single-grid-icon {
        background-color: rgba(76, 175, 80, 0.1);
    }

    .total-customers .single-grid-icon svg {
        fill: #4CAF50;
    }

    .info-box {
        display: flex;
        justify-content: space-between;
        min-height: 100px;
        margin-bottom: 20px;
        padding: 15px;
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .bg-primary {
        background-color: #4e73df;
    }
    .bg-danger {
        background-color: #ff5a8d;
    }
    .bg-warning {
        background-color: #ff7d4a;
    }
    .bg-success {
        background-color: #1cc88a;
    }
    .info-box-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .info-box-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        width: 60px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.2);
        height: 60px;
        color: white;
    }
    .info-box-icon svg {
        width: 28px;
        height: 28px;
        display: inline-block;
        vertical-align: middle;
    }
    .info-box-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .info-box-text {
        font-size: 0.9rem;
        text-transform: uppercase;
        font-weight: 500;
    }
    .mt-4 {
        margin-top: 1.5rem;
    }

    /* Box styling */
    .box {
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        background-color: #fff;
        margin-bottom: 20px;
    }
    .box-header {
        padding: 15px;
        border-bottom: 1px solid #f1f1f1;
    }
    .box-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #333;
    }
    .box-body {
        padding: 15px;
    }

    /* Table styling */
    .table-borderless {
        margin-bottom: 0;
    }
    .table-borderless td, .table-borderless th {
        border: none;
        padding: 12px 15px;
        vertical-align: middle;
        border-bottom: none !important;
    }
    .brands-header th, .products-header th, .users-header th {
        color: #666;
        font-weight: 600;
        border-bottom: 1px solid #f1f1f1 !important;
        background-color: #f9f9f9;
    }

    /* Thêm hover effect */
    .table-borderless tbody tr {
        cursor: pointer;

    }

    .table-borderless tbody tr:hover {
        background-color: rgba(33, 150, 243, 0.05);

    }

    /* Cập nhật hover cho text */
    .table-borderless tbody tr td {

    }

    .table-borderless tbody tr:hover td {
        color: #2196F3;
    }

    /* Cập nhật style cho status badges theo hình */
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
        min-width: 80px;
        text-align: center;
        vertical-align: middle;
        font-weight: 500;
    }

    /* Cập nhật màu sắc status badge theo màu vàng và xanh dương */
    .status-badge.pending-payment,
    .status-badge.cancelled,
    .status-badge.inactive,
    .status-badge.disabled {
        background-color: #fff3cd;
        color: #ffc107;
    }

    .status-badge.pending,
    .status-badge.active,
    .status-badge.enabled,
    .status-badge.completed {
        background-color: #cfe2ff;
        color: #0d6efd;
    }

    .status-badge.role-admin {
        background-color: #fff3cd;
        color: #ffc107;
    }

    .status-badge.role-member,
    .status-badge.role-user {
        background-color: #cfe2ff;
        color: #0d6efd;
    }

    .status-badge.default {
        background-color: #f0f0f0;
        color: #666;
    }

    /* No data message */
    .no-data {
        color: #999;
        font-style: italic;
        padding: 20px 0;
    }
    .no-data td {
        border-bottom: none !important;
    }

    /* Chart container */
    .product-price-chart .chart {
        width: 100%;
        height: 300px !important;
    }
</style>
@endpush

@push('globals')
    @vite([
        "modules/Admin/Resources/assets/sass/dashboard.scss",
        "modules/Admin/Resources/assets/js/dashboard.js",
    ])
@endpush
