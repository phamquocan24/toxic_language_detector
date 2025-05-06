<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>@yield('title', 'Đăng nhập') | {{ config('app.name', 'Toxic Detector') }}</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Styles -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary-color: #5e72e4;
            --secondary-color: #f7fafc;
            --dark-color: #172b4d;
            --light-color: #f6f9fc;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--light-color);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .auth-wrapper {
            width: 100%;
            padding: 2rem 1rem;
        }
        
        .auth-card {
            max-width: 400px;
            margin: 0 auto;
            border: none;
            box-shadow: 0 0 2rem 0 rgba(136, 152, 170, .15);
            border-radius: 0.5rem;
            overflow: hidden;
        }
        
        .auth-card .card-header {
            background-color: var(--primary-color);
            color: white;
            border-bottom: none;
            padding: 1.5rem;
            font-weight: 600;
            font-size: 1.2rem;
            text-align: center;
        }
        
        .auth-card .card-body {
            padding: 2rem;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            padding: 0.6rem 1rem;
        }
        
        .btn-primary:hover {
            background-color: #324cdd;
            border-color: #324cdd;
        }
        
        .form-control {
            border-radius: 0.375rem;
            padding: 0.75rem 1rem;
            border-color: #e9ecef;
        }
        
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(94, 114, 228, 0.25);
        }
        
        .input-group-text {
            background-color: white;
            border-right: none;
        }
        
        .input-group .form-control {
            border-left: none;
        }
        
        .logo-wrapper {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo-wrapper img {
            height: 70px;
            margin-bottom: 1rem;
        }
        
        .logo-wrapper h1 {
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        
        .logo-wrapper p {
            color: #8898aa;
            font-size: 1rem;
            margin-bottom: 0;
        }
    </style>
    
    @stack('styles')
</head>
<body>
    <div class="auth-wrapper">
        <div class="container">
            <div class="logo-wrapper">
                <i class="fas fa-shield-alt fa-3x text-primary"></i>
                <h1>{{ config('app.name', 'Toxic Detector') }}</h1>
                <p>Phát hiện ngôn ngữ độc hại</p>
            </div>
            
            @yield('content')
            
            <div class="text-center mt-4">
                <p class="text-muted">
                    &copy; {{ date('Y') }} {{ config('app.name', 'Toxic Detector') }}
                </p>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    @stack('scripts')
</body>
</html> 