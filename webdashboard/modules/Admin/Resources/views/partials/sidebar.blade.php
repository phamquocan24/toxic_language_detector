<aside class="main-sidebar">
    <header class="main-header clearfix">
        <a class="logo" href="{{ route('admin.dashboard.index') }}">
            <img src="{{ asset('build/assets/sidebar-logo-ltr.svg') }}" alt="sidebar logo">
        </a>

        <a class="sidebar-logo-mini" href="{{ route('admin.dashboard.index') }}">
            <img src="{{ asset('build/assets/sidebar-logo-mini.svg') }}" alt="sidebar logo mini">
        </a>

        <a href="javascript:void(0);" class="sidebar-toggle" data-toggle="offcanvas" role="button">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M15.0001 19.92L8.48009 13.4C7.71009 12.63 7.71009 11.37 8.48009 10.6L15.0001 4.07996"
                      stroke="#292D32" stroke-width="3" stroke-miterlimit="10" stroke-linecap="round"
                      stroke-linejoin="round" />
            </svg>

            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="150px" height="150px">
                <path
                    d="M 3 9 A 1.0001 1.0001 0 1 0 3 11 L 47 11 A 1.0001 1.0001 0 1 0 47 9 L 3 9 z M 3 24 A 1.0001 1.0001 0 1 0 3 26 L 47 26 A 1.0001 1.0001 0 1 0 47 24 L 3 24 z M 3 39 A 1.0001 1.0001 0 1 0 3 41 L 47 41 A 1.0001 1.0001 0 1 0 47 39 L 3 39 z" />
            </svg>
        </a>
    </header>
    <section class="sidebar">
        <ul class="sidebar-menu">
            <li class="{{ activeMenu('')['main'] }}">
                <a href="{{ route('admin.dashboard.index') }}" class="">
                    <i class="fa fa-dashboard"></i>
                    <span>Dashboard</span>
                </a>
            </li>

            <li class="treeview {{ activeMenu('comments')['main'] }} ">
                <a href="{{ route('admin.comments.index') }}" class="">
                    <i class="fa fa-comments-o"></i>
                    <span>Hate Speech Detection</span>
                    <span class="pull-right-container">
                        <i class="fa fa-angle-left pull-right"></i>
                    </span>
                </a>
                <ul class="treeview-menu">
                    <li class="{{ activeMenu('comments', 'create')['sub'] }}">
                        <a href="{{ route('admin.comments.create') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Create Comments</span>
                        </a>
                    </li>
                    <li class="{{ activeMenu('comments')['sub'] }}">
                        <a href="{{ route('admin.comments.index') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>All Comments</span>
                        </a>
                    </li>
                </ul>
            </li>
            <li class="treeview {{ activeMenu('prediction')['main'] }}">
                <a href="{{ route('admin.prediction.batch') }}" class="">
                    <i class="fa fa-flask"></i>
                    <span>Prediction</span>
                    <span class="pull-right-container">
                        <i class="fa fa-angle-left pull-right"></i>
                    </span>
                </a>
                <ul class="treeview-menu">
                    <li class="{{ activeMenu('prediction.batch')['sub'] }}">
                        <a href="{{ route('admin.prediction.batch') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Batch Prediction</span>
                        </a>
                    </li>
                    <li class="{{ activeMenu('prediction.upload')['sub'] }}">
                        <a href="{{ route('admin.prediction.upload') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Upload CSV File</span>
                        </a>
                    </li>
                    <li class="{{ activeMenu('prediction.similar')['sub'] }}">
                        <a href="{{ route('admin.prediction.similar') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Similar Comments</span>
                        </a>
                    </li>
                </ul>
            </li>
            <li class="treeview {{ activeMenu('feedbacks')['main'] }}">
                <a href="{{ route('admin.feedbacks.index') }}" class="">
                    <i class="fa fa-bar-chart"></i>
                    <span>Feedbacks</span>
                    <span class="pull-right-container">
                        <i class="fa fa-angle-left pull-right"></i>
                    </span>
                </a>
                <ul class="treeview-menu">
                    <li class="{{ activeMenu('feedbacks')['sub'] }}">
                        <a href="{{ route('admin.feedbacks.index') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Report</span>
                        </a>
                    </li>
                </ul>
            </li>
            <li class="treeview {{ activeMenu('users')['main'] }} ">
                <a href="{{ route('admin.users.index') }}" class="">
                    <i class="fa fa-users"></i>
                    <span>Users</span>
                    <span class="pull-right-container">
                        <i class="fa fa-angle-left pull-right"></i>
                    </span>
                </a>
                <ul class="treeview-menu">
                    <li class="{{ activeMenu('users')['sub'] }}">
                        <a href="{{ route('admin.users.index') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>All Users</span>
                        </a>
                    </li>
                    <li class="{{ activeMenu('users', 'create')['sub'] }}">
                        <a href="{{ route('admin.users.create') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>Create Users</span>
                        </a>
                    </li>
                </ul>
            </li>
            <li class="treeview {{ activeMenu('logs')['main'] }} ">
                <a href="{{ route('admin.logs.index') }}" class="">
                    <i class="fa fa-cogs"></i>
                    <span>Logs</span>
                    <span class="pull-right-container">
                        <i class="fa fa-angle-left pull-right"></i>
                    </span>
                </a>
                <ul class="treeview-menu">
                    <li class="{{ activeMenu('logs')['sub'] }}">
                        <a href="{{ route('admin.logs.index') }}" class="">
                            <i class="fa fa-angle-double-right"></i>
                            <span>System Logs</span>
                        </a>
                    </li>
                </ul>
            </li>
        </ul>
    </section>
</aside>
