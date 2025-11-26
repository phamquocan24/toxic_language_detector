<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'mailgun' => [
        'domain' => env('MAILGUN_DOMAIN'),
        'secret' => env('MAILGUN_SECRET'),
        'endpoint' => env('MAILGUN_ENDPOINT', 'api.mailgun.net'),
        'scheme' => 'https',
    ],

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],
    'toxic_detection' => [
        'url' => env('TOXIC_API_URL', 'http://localhost:7860'),
        'token_url' => env('TOXIC_TOKEN_URL', '/auth/token'),
        'auth_header' => env('TOXIC_AUTH_HEADER', 'Authorization'),
        'auth_type' => env('TOXIC_AUTH_TYPE', 'Bearer'),
        'oauth' => [
            'username' => env('TOXIC_OAUTH_USERNAME'),
            'password' => env('TOXIC_OAUTH_PASSWORD'),
            'client_id' => env('TOXIC_OAUTH_CLIENT_ID'),
            'client_secret' => env('TOXIC_OAUTH_CLIENT_SECRET'),
        ],
    ],
    'backend' => [
        'url' => env('BACKEND_API_URL', 'http://localhost:8000'),
        'timeout' => env('BACKEND_API_TIMEOUT', 30),
        'auth_header' => env('BACKEND_AUTH_HEADER', 'Authorization'),
        'auth_type' => env('BACKEND_AUTH_TYPE', 'Bearer'),
    ],
];
