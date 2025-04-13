import Chart from "chart.js/auto";

class Dashboard {
    constructor() {
        this.apiEndpoints = {
            productPrices: '/admin/api/dashboard/product-prices',
            latestProducts: '/admin/api/dashboard/latest-products',
            latestBrands: '/admin/api/dashboard/latest-brands',
            latestUsers: '/admin/api/dashboard/latest-users',
            stats: '/admin/api/dashboard/stats'
        };

        this.routes = {
            products: '/admin/products',
            brands: '/admin/brands',
            users: '/admin/users'
        };

        this.initComponents();
    }

    initComponents() {
        this.fetchData();
    }

    // Fetch data from API endpoints
    fetchData() {
        this.initStatCards();
        this.fetchProductPriceData();
        this.fetchLatestProducts();
        this.fetchLatestBrands();
        this.fetchLatestUsers();
        this.fetchDashboardStats();
    }

    // Fetch dashboard stats
    fetchDashboardStats() {
        $.ajax({
            url: this.apiEndpoints.stats,
            method: 'GET',
            success: (response) => {
                if (response && response.data) {
                    this.updateStatCards(response.data);
                }
            },
            error: (error) => {
                console.error('Error fetching dashboard stats:', error);
            }
        });
    }

    // Fetch product price data
    fetchProductPriceData() {
        $.ajax({
            url: this.apiEndpoints.productPrices,
            method: 'GET',
            success: (response) => {
                if (response && response.success && response.data && response.data.length > 0) {
                    const chartData = {
                        labels: response.data.map(p => p.name),
                        prices: response.data.map(p => p.price),
                        formattedPrices: response.data.map(p => p.formatted_price),
                        priceRanges: response.data.map(p => p.price_range)
                    };
                    this.initProductPriceChart(chartData);
                } else {
                    console.warn("No product price data received from API");
                    // Hiển thị thông báo không có dữ liệu
                    const canvas = $(".product-price-chart .chart").get(0);
                    if (canvas) {
                        const ctx = canvas.getContext('2d');
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.textAlign = 'center';
                        ctx.fillText('No product price data available.', canvas.width / 2, canvas.height / 2);
                    }
                }
            },
            error: (error) => {
                console.error('Error fetching product price data:', error);
                // Hiển thị thông báo lỗi
                const canvas = $(".product-price-chart .chart").get(0);
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.textAlign = 'center';
                    ctx.fillText('Error loading product price data.', canvas.width / 2, canvas.height / 2);
                }
            }
        });
    }

    // Fetch latest products
    fetchLatestProducts() {
        $.ajax({
            url: this.apiEndpoints.latestProducts,
            method: 'GET',
            success: (response) => {
                if (response && response.data && response.data.length > 0) {
                    this.renderLatestProducts(response.data);
                }
            },
        });
    }

    // Fetch latest brands
    fetchLatestBrands() {
        $.ajax({
            url: this.apiEndpoints.latestBrands,
            method: 'GET',
            success: (response) => {
                if (response && response.data && response.data.length > 0) {
                    this.renderLatestBrands(response.data);
                }
            },
            error: (error) => {
                console.error('Error fetching latest brands:', error);
            }
        });
    }

    // Fetch latest users
    fetchLatestUsers() {
        console.log('Fetching latest users from:', this.apiEndpoints.latestUsers);

        $.ajax({
            url: this.apiEndpoints.latestUsers,
            method: 'GET',
            success: (response) => {
                console.log('Latest users API response:', response);

                if (response && response.success && response.data) {
                    this.latestUsers = response.data;
                    this.renderLatestUsers(this.latestUsers);
                } else {
                    console.error('Invalid response format from API:', response);
                    this.renderLatestUsers([]);
                }
            },
            error: (error) => {
                console.error('Error fetching latest users:', error);
                this.renderLatestUsers([]);
            }
        });
    }

    // Khởi tạo các thẻ thống kê
    initStatCards() {
        this.updateStatCards({
            totalSales: '71.09K',
            totalOrders: '46',
            totalProducts: '140',
            totalCustomers: '4'
        });
    }

    // Cập nhật giá trị cho các thẻ thống kê
    updateStatCards(data) {
        if (data.totalSales) $('#total-sales').text(data.totalSales);
        if (data.totalOrders) $('#total-orders').text(data.totalOrders);
        if (data.totalProducts) $('#total-products').text(data.totalProducts);
        if (data.totalCustomers) $('#total-customers').text(data.totalCustomers);
    }

    // --- 1. Biểu đồ giá sản phẩm ---
    loadProductPriceChart() {
        let chartData = {
            labels: this.productPrices.map(p => p.name),
            prices: this.productPrices.map(p => p.price),
            formattedPrices: this.productPrices.map(p => p.formatted_price),
        };
        this.initProductPriceChart(chartData);
    }

    // Khởi tạo biểu đồ giá sản phẩm
    initProductPriceChart(data) {
        if (!data || !data.labels || data.labels.length === 0) {
            console.warn("No data provided for product price chart.");
            const canvas = $(".product-price-chart .chart").get(0);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.textAlign = 'center';
                ctx.fillText('No product price data available.', canvas.width / 2, canvas.height / 2);
            }
            return;
        }

        // Màu sắc tương ứng với các mức giá
        const backgroundColors = [
            "rgba(136, 194, 115, .7)",  // Normal - Xanh lá
            "rgba(76, 201, 254, .7)",   // Middle - Xanh dương
            "rgba(255, 127, 62, .7)",   // Premium - Cam
            "rgba(255, 119, 183, .7)"   // Luxury - Hồng
        ];

        new Chart($(".product-price-chart .chart"), {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Number of Products',
                        data: data.prices,
                        borderRadius: 6,
                        backgroundColor: backgroundColors.slice(0, data.labels.length),
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            label: (item) => {
                                return `${data.labels[item.dataIndex]}: ${data.formattedPrices[item.dataIndex]}`;
                            },
                            afterLabel: (item) => {
                                return `Price Range: ${data.priceRanges[item.dataIndex]}`;
                            }
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Products'
                        },
                        ticks: {
                            precision: 0
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Price Categories'
                        }
                    }
                },
            },
        });
    }


    // --- 2. Sản phẩm mới nhất ---
    loadLatestProducts() {
        this.renderLatestProducts(this.latestProducts);
    }

    // Hiển thị dữ liệu sản phẩm mới nhất
    renderLatestProducts(products) {
        const $tableBody = $('#latest-products-table tbody');
        $tableBody.empty();

        if (!products || products.length === 0) {
            $tableBody.append(`<tr><td colspan="4" class="text-center no-data">No products available!</td></tr>`);
            return;
        }

        products.forEach(product => {
            const statusClass = product.status_class || (product.status && product.status.toLowerCase() === 'active' ? 'active' : 'inactive');
            const statusText = product.status || 'N/A';

            const $row = $(`
                <tr data-id="${product.id}">
                    <td>${product.name}</td>
                    <td>${product.sku}</td>
                    <td>${product.formatted_price || product.price}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                </tr>
            `);

            // Add click handler to redirect to products index page
            $row.on('click', () => {
                window.location.href = this.routes.products;
            });

            $tableBody.append($row);
        });
    }


    // --- 3. Thương hiệu mới nhất ---
    loadLatestBrands() {
        this.renderLatestBrands(this.latestBrands);
    }

    // Hiển thị dữ liệu thương hiệu
    renderLatestBrands(brands) {
        const $tableBody = $('#latest-brands-table tbody');
        $tableBody.empty();

        if (!brands || brands.length === 0) {
             $tableBody.append(`<tr><td colspan="3" class="text-center no-data">No brands available!</td></tr>`);
            return;
        }

        brands.forEach(brand => {
            const statusClass = brand.status_class ||
        (brand.status && brand.status.toLowerCase() === 'enabled' ? 'enabled' : 'disabled');


            const statusText = brand.status_text || brand.status || 'N/A';

            const $row = $(`
                <tr data-id="${brand.id}">
                    <td>${brand.name}</td>
                    <td>${brand.products_count}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                </tr>
            `);

            // Add click handler to redirect to brands index page
            $row.on('click', () => {
                window.location.href = this.routes.brands;
            });

            $tableBody.append($row);
        });
    }

    // --- 4. Người dùng mới nhất ---
    loadLatestUsers() {
        this.renderLatestUsers(this.latestUsers);
    }

    // Hiển thị dữ liệu người dùng mới nhất
    renderLatestUsers(users) {
        const $tableBody = $('#latest-users-table tbody');
        $tableBody.empty();

        if (!users || users.length === 0) {
            $tableBody.append(`<tr><td colspan="3" class="text-center no-data">Không có người dùng mới!</td></tr>`);
            return;
        }

        users.forEach(user => {
            // Sử dụng status_class và status từ API nếu có
            const statusClass = user.status_class || (user.role === 1 ? 'role-admin' : 'role-member');

            const statusText = user.status || user.role_text || 'N/A';

            const $row = $(`
                <tr data-id="${user.id}">
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.email}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                </tr>
            `);

            // Thêm sự kiện click để chuyển đến trang chi tiết người dùng
            $row.on('click', () => {
                window.location.href = this.routes.users;
            });

            $tableBody.append($row);
        });
    }
}

// Khởi tạo Dashboard khi trang đã tải xong
$(function() {
    window.dashboard = new Dashboard();
});
