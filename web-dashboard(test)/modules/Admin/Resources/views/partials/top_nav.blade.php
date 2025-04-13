<nav class="navbar navbar-static-top clearfix">
    <ul class="nav navbar-nav clearfix">
        <li class="user dropdown top-nav-menu pull-right">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                <span>Admin Panel</span>
                <div class="dropdown-arrow-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="9" viewBox="0 0 18 9" fill="none">
                        <path d="M16.9201 0.949951L10.4001 7.46995C9.63008 8.23995 8.37008 8.23995 7.60008 7.46995L1.08008 0.949951" stroke="#292D32" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </a>

            <ul class="dropdown-menu">
                <li class="profile-details">
                    <span class="profile-first-letter">Admin Panel</span>

                    <div class="profile-info">
                        <h4>
                            <span>Admin Panel</span>

                            <span>Admin</span>
                        </h4>

                        <span class="profile-email">admin@gmail.com</span>
                    </div>
                </li>

                <li>
                    <a href="{{ route('admin.profile') }}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M20.5899 22C20.5899 18.13 16.7399 15 11.9999 15C7.25991 15 3.40991 18.13 3.40991 22" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                       Profile
                    </a>
                </li>

                <li>
                    <form id="logout-form" action="{{ route('auth.logout') }}" method="GET" style="display: none;">
                        @csrf
                    </form>
                    <a href="#" onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M17.4399 14.62L19.9999 12.06L17.4399 9.5" stroke="#292D32" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M9.76001 12.0601H19.93" stroke="#292D32" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M11.76 20C7.34001 20 3.76001 17 3.76001 12C3.76001 7 7.34001 4 11.76 4" stroke="#292D32" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Logout
                    </a>
                </li>
            </ul>
        </li>
        <li class="fullscreen-mode">
            <a class="fullscreen-mode-open" href="#">
                <svg class="fullscreen-one exit-full-screen" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5,5H10V7H7V10H5V5M14,5H19V10H17V7H14V5M17,14H19V19H14V17H17V14M10,17V19H5V14H7V17H10Z"/></svg>
                <svg class="fullscreen-two" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14,14H19V16H16V19H14V14M5,14H10V19H8V16H5V14M8,5H10V10H5V8H8V5M19,8V10H14V5H16V8H19Z"/></svg>
            </a>
        </li>
    </ul>
</nav>
