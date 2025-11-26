<?php

namespace Modules\User\Entities;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;
use Carbon\Carbon;

class InvitationToken extends Model
{
    protected $fillable = ['email', 'token', 'role', 'expires_at', 'accepted_at'];

    protected $casts = [
        'created_at' => 'datetime',
        'expires_at' => 'datetime',
        'accepted_at' => 'datetime',
    ];

    public $timestamps = false;

    protected static function booted()
    {
        static::creating(function ($token) {
            $token->token = Str::random(64);
            $token->created_at = Carbon::now();
            $token->expires_at = Carbon::now()->addDays(7);
        });
    }

    public function isExpired()
    {
        return Carbon::parse($this->expires_at)->isPast();
    }

    public function isAccepted()
    {
        return $this->accepted_at !== null;
    }
}
