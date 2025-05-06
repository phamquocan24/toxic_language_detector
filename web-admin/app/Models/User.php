<?php

namespace App\Models;

use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    /** @use HasFactory<\Database\Factories\UserFactory> */
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'id',
        'name',
        'username',
        'email',
        'role',
        'is_admin',
        'password',
        'is_active',
        'api_token',
        'extension_id',
        'last_login_at',
        'profile_photo',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
        'is_active' => 'boolean',
        'last_login_at' => 'datetime',
    ];

    /**
     * Get the comments for the user.
     */
    public function comments()
    {
        return $this->hasMany(Comment::class);
    }

    /**
     * Check if user is admin from either role or is_admin attribute
     * 
     * @return bool
     */
    public function getIsAdminAttribute()
    {
        // Support both formats from the API:
        // 1. Explicit is_admin property
        if (isset($this->attributes['is_admin'])) {
            return (bool) $this->attributes['is_admin'];
        }
        
        // 2. Role being admin
        if (isset($this->attributes['role'])) {
            if (is_array($this->attributes['role'])) {
                if (isset($this->attributes['role']['name'])) {
                    return $this->attributes['role']['name'] === 'admin';
                }
            } else {
                return $this->attributes['role'] === 'admin';
            }
        }
        
        return false;
    }

    /**
     * Check if the user is a regular user.
     *
     * @return bool
     */
    public function isUser()
    {
        return $this->role === 'user';
    }

    /**
     * Get the profile photo URL.
     *
     * @return string
     */
    public function getProfilePhotoUrlAttribute()
    {
        if ($this->profile_photo) {
            return asset('storage/' . $this->profile_photo);
        }
        
        return asset('images/default-avatar.png');
    }

    /**
     * Count comments by classification.
     *
     * @param string $classification
     * @return int
     */
    public function countCommentsByClassification($classification)
    {
        return $this->comments()->where('classification', $classification)->count();
    }

    /**
     * Get the stats for the user.
     *
     * @return array
     */
    public function getStats()
    {
        return [
            'total_comments' => $this->comments()->count(),
            'clean_comments' => $this->countCommentsByClassification('clean'),
            'offensive_comments' => $this->countCommentsByClassification('offensive'),
            'hate_comments' => $this->countCommentsByClassification('hate'),
            'spam_comments' => $this->countCommentsByClassification('spam'),
        ];
    }

    /**
     * Scope a query to only include active users.
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }

    /**
     * Scope a query to only include admin users.
     */
    public function scopeAdmins($query)
    {
        return $query->where('role', 'admin');
    }

    /**
     * Scope a query to only include regular users.
     */
    public function scopeRegularUsers($query)
    {
        return $query->where('role', 'user');
    }
}

