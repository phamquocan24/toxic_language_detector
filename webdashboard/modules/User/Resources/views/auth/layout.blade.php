<!DOCTYPE html>
<html lang="{{ locale() }}">
    <head>
        <base href="{{ url('/') }}">
        <meta charset="UTF-8">

        <title>
            @yield('title')
        </title>

        <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

        @vite([
            'modules/User/Resources/assets/sass/pages/auth/main.scss',
            'modules/User/Resources/assets/js/pages/auth/main.js',
        ])

        @stack('globals')
    </head>

    <body class="clearfix ltr" dir="ltr">
        <div class="login-page">
            @yield('content')
        </div>
    </body>
</html>
