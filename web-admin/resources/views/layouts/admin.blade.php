<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'Dashboard') | Toxic Detector Admin</title>

    <!-- Google Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- DataTables -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css">
    
    <style>
        :root {
            --primary-color: #5e72e4;
            --secondary-color: #f7fafc;
            --dark-color: #172b4d;
            --dark-sidebar: #1e1e2d;
            --light-color: #f6f9fc;
            --text-muted: #9ca8b3;
            --success-color: #4fd1c5;
            --warning-color: #fb6340;
            --danger-color: #f5365c;
            --info-color: #11cdef;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--light-color);
            margin: 0;
            font-size: 0.875rem;
        }
        
        /* Sidebar Styles */
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: 240px;
            height: 100%;
            background-color: var(--dark-sidebar);
            color: #fff;
            overflow-y: auto;
            z-index: 100;
            transition: all 0.3s;
        }
        
        .sidebar-brand {
            display: flex;
            align-items: center;
            padding: 1rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            height: 65px;
        }
        
        .sidebar-brand h3 {
            color: #fff;
            margin: 0;
            font-weight: 600;
            font-size: 1.25rem;
            margin-left: 10px;
        }
        
        .sidebar-menu {
            padding: 0;
            list-style: none;
            margin-bottom: 1rem;
        }
        
        .sidebar-item {
            margin-bottom: 0.25rem;
        }
        
        .sidebar-link {
            display: flex;
            align-items: center;
            padding: 0.75rem 1.25rem;
            font-size: 0.875rem;
            color: var(--text-muted);
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .sidebar-link:hover {
            color: #fff;
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .sidebar-link.active {
            color: #fff;
            background-color: rgba(255, 255, 255, 0.1);
            border-left: 3px solid var(--primary-color);
        }
        
        .sidebar-icon {
            margin-right: 0.75rem;
            width: 20px;
            text-align: center;
        }
        
        .sidebar-heading {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
            color: var(--text-muted);
            padding: 0.75rem 1.25rem;
            margin-top: 1rem;
        }
        
        /* Main Content Styles */
        .content-wrapper {
            margin-left: 240px;
            padding: 0;
            min-height: 100vh;
            background-color: var(--light-color);
            transition: all 0.3s;
        }
        
        .main-header {
            background-color: #fff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 0.75rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 65px;
        }
        
        .header-title {
            font-weight: 600;
            font-size: 1.5rem;
            color: var(--dark-color);
        }
        
        .user-menu {
            display: flex;
            align-items: center;
        }
        
        .language-dropdown {
            margin-right: 1rem;
        }
        
        .user-dropdown img {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        /* Dashboard Widgets */
        .dashboard-card {
            border-radius: 0.5rem;
            border: none;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            height: 100%;
            background: #fff;
        }
        
        .stats-card {
            border-radius: 0.5rem;
            padding: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .stats-card.primary {
            background-color: #6366f1;
            color: #fff;
        }
        
        .stats-card.info {
            background-color: #06b6d4;
            color: #fff;
        }
        
        .stats-card.success {
            background-color: #22c55e;
            color: #fff;
        }
        
        .stats-card.warning {
            background-color: #f59e0b;
            color: #fff;
        }
        
        .stats-card .icon {
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .stats-card .icon i {
            font-size: 1.5rem;
        }
        
        .stats-card .stats-content {
            text-align: left;
        }
        
        .stats-card .stats-title {
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            opacity: 0.8;
        }
        
        .stats-card .stats-number {
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0;
        }
        
        /* Table Styles */
        .table-heading {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .table-heading h5 {
            font-weight: 600;
            margin-bottom: 0;
        }
        
        .table th {
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            border-top: none;
        }
        
        .table td {
            vertical-align: middle;
            font-size: 0.875rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.75rem;
            font-weight: 500;
            border-radius: 0.375rem;
        }
        
        .status-badge.pending {
            background-color: rgba(246, 153, 63, 0.1);
            color: #f6993f;
        }
        
        .status-badge.completed {
            background-color: rgba(56, 193, 114, 0.1);
            color: #38c172;
        }
        
        .btn-action {
            padding: 0.375rem 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        /* Main Content Area */
        .main-content {
            padding: 1.5rem;
        }
        
        /* Alert Styles */
        .alert {
            border-radius: 0.5rem;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            border: none;
        }
        
        /* Card Headers */
        .card-header {
            background-color: #fff;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            padding: 1rem 1.5rem;
        }
        
        .card-header h5 {
            margin-bottom: 0;
            font-weight: 600;
        }
        
        /* Footer Styles */
        .main-footer {
            padding: 1rem 1.5rem;
            font-size: 0.875rem;
            color: var(--text-muted);
            background-color: #fff;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            margin-left: 240px;
        }
    </style>
    
    @stack('styles')
</head>

<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-brand">
            <i class="fas fa-shield-alt"></i>
            <h3>Toxic Detector</h3>
        </div>
        
        <ul class="sidebar-menu">
            <li class="sidebar-item">
                <a href="{{ route('admin.dashboard') }}" class="sidebar-link {{ request()->routeIs('admin.dashboard') ? 'active' : '' }}">
                    <span class="sidebar-icon"><i class="fas fa-tachometer-alt"></i></span>
                    <span>Dashboard</span>
                </a>
            </li>
            
            <li class="sidebar-item">
                <a href="{{ route('admin.comments.index') }}" class="sidebar-link {{ request()->routeIs('admin.comments*') ? 'active' : '' }}">
                    <span class="sidebar-icon"><i class="fas fa-comment"></i></span>
                    <span>Bình luận</span>
                </a>
            </li>
            
            <li class="sidebar-item">
                <a href="{{ route('admin.users.index') }}" class="sidebar-link {{ request()->routeIs('admin.users*') ? 'active' : '' }}">
                    <span class="sidebar-icon"><i class="fas fa-users"></i></span>
                    <span>Người dùng</span>
                </a>
            </li>
            
            <div class="sidebar-heading">Hệ thống</div>
            
            @if (Route::has('admin.settings.index'))
            <li class="sidebar-item">
                <a href="{{ route('admin.settings.index') }}" class="sidebar-link {{ request()->routeIs('admin.settings*') ? 'active' : '' }}">
                    <span class="sidebar-icon"><i class="fas fa-cog"></i></span>
                    <span>Cài đặt</span>
                </a>
            </li>
            @endif
        </ul>
    </div>

    <!-- Main Content -->
    <div class="content-wrapper">
        <!-- Header -->
        <header class="main-header">
            <div class="header-title">@yield('title', 'Dashboard')</div>
            
            <div class="user-menu">
                <div class="language-dropdown dropdown">
                    <button class="btn btn-sm btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <span>EN</span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#">English</a></li>
                        <li><a class="dropdown-item" href="#">Tiếng Việt</a></li>
                    </ul>
                </div>
                
                <div class="user-dropdown dropdown">
                    <a href="#" class="text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
                        <img src="https://ui-avatars.com/api/?name={{ Auth::user()->name }}&background=random" alt="User">
                        <span class="d-none d-md-inline-block">{{ Auth::user()->name }}</span>
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i> Hồ sơ</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item" href="{{ route('logout') }}"
                               onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                                <i class="fas fa-sign-out-alt me-2"></i> Đăng xuất
                            </a>
                            <form id="logout-form" action="{{ route('logout') }}" method="POST" class="d-none">
                                @csrf
                            </form>
                        </li>
                    </ul>
                </div>
            </div>
        </header>
        
        <!-- Main Content Area -->
        <div class="main-content">
            @if(session('success'))
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                {{ session('success') }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            @endif

            @if(session('error'))
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ session('error') }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            @endif
            
            @yield('content')
        </div>
        
        <!-- Footer -->
        <footer class="main-footer">
            <div class="d-flex justify-content-between">
                <div>
                    <strong>Toxic Detector Admin &copy; {{ date('Y') }}</strong>
                </div>
                <div class="d-none d-sm-inline-block">
                    <b>Version</b> 1.0.0
                </div>
            </div>
        </footer>
    </div>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js"></script>
    
    @stack('scripts')
</body>
</html> 